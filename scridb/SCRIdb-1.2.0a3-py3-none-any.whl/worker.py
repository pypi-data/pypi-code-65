#!/usr/bin/env python3

import datetime
from datetime import date

import mysql
from tabulate import tabulate

from .query import run
from .tools import *


def worker_main(
    f_in: Union[str, list],
    source_path: str = None,
    target_path: str = None,
    runseqc: bool = True,
    hashtag: bool = True,
    vdj: bool = True,
    atac: bool = True,
    cr: bool = True,
    no_rsync: bool = False,
    save: bool = False,
    **args
) -> None:
    """\
    A method to process raw sequencing data returned from **IGO**. Newly sequenced
    samples are copied from IGO shared drive to a defined `S3URI`. Then, the proper
    pipeline is called to process the copied raw data.

    :param f_in:
        Input file name, a single sample name, or a list of sample names, sequenced and
        ready to be processed.
    :param source_path:
        Source path to parent directory of sequenced samples, usually an IGO shared
        drive.
    :param target_path:
        Target path to parent directory of sequenced samples, usually, a `S3URI`.
    :param runseqc:
        Call `seqc` pipeline. Default: `True`.
    :param hashtag:
        Call `hashtag` pipeline. Default: `True`.
    :param vdj:
        Call `VDJ` pipeline. Default: `True`.
    :param atac:
        Call `atac-seq` pipeline. Default: `True`.
    :param cr:
        Call `Cell Ranger` pipeline. Default: `True`.
    :param no_rsync:
        Skip copying files to `S3`.
    :param save:
        Write `sample_data` to `.csv` output configured in `--results_output`.
    :param args:
        Additional args passed to other methods.

    :return:
        `None`.

    Example
    =======

    >>> from SCRIdb.worker import *
    >>> args = json.load(open(os.path.expanduser("~/.config.json")))
    >>> args["jobs"] = "jobs.yml"
    >>> args["seqcargs"] = {"min-poly-t": 0}
    >>> db_connect.conn(args)
    >>> worker_main(
        f_in=[
                "Sample_CCR7_DC_1_IGO_10587_12",
                "Sample_CCR7_DC_2_IGO_10587_13",
                "Sample_CCR7_DC_3_IGO_10587_14",
                "Sample_CCR7_DC_4_IGO_10587_15"
        ],
        source_path="/Volumes/peerd/FASTQ/Project_10587/MICHELLE_0194",
        target_path="s3://dp-lab-data/sc-seq/Project_10587",
        runseqc = False,
        no_rsync = True,
        **args
    )
    """

    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s: %(asctime)s: %(message)s")

    fh = logging.FileHandler("processing.log")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    print("Processing new fastq files ...")

    # read in delivery report
    if isinstance(f_in, list):
        f_in = " ".join(f_in)
    if os.path.isfile(f_in):
        sd = pd.read_csv(f_in, index_col=0)
    elif f_in == "-":
        print(
            "Fill in the Sample ID/s and Sample name/s below, comma or tab "
            "separated:"
        )
        sample_ids = input("\n\nSample ID/s: ")
        if not sample_ids:
            print("Try again:")
            sample_ids = input("\n\nSample ID/s: ")
            if not sample_ids:
                print("Missing Sample ID/s!!")
                sys.exit(1)

        sample_names = input("\n\nSample name/s: ")
        if not sample_names:
            print("Try again:")
            sample_names = input("\n\nSample name/s: ")
            if not sample_names:
                print("Missing Sample name/s!!")
                sys.exit(1)

        sample_ids = re.sub(",", " ", sample_ids.strip()).split()
        sample_names = re.sub(",", " ", sample_names.strip()).split()

        # Collect data from the database
        stmt = (
            "SELECT `id`, `Sample`, `source_path`, `AWS_storage` "
            "FROM `sample_data` WHERE `id`=%s AND `Sample`=%s "
            "UNION "
            "SELECT `sampleData_id`, `Sample`, `source_path`, `AWS_storage` "
            "FROM `hashtag_lib` WHERE `sampleData_id`=%s AND `Sample`=%s "
            "UNION "
            "SELECT `sampleData_id`, `Sample`, `source_path`, `AWS_storage` "
            "FROM `TCR_lib` WHERE `sampleData_id`=%s AND `Sample`=%s"
        )
        results = []
        for items in zip(sample_ids, sample_names):
            db_connect.cur.execute(stmt, items * 3)
            res = db_connect.cur.fetchall()
            if res:
                try:
                    assert res[0][2], "AssertionError: Missing S3URI!"
                    assert res[0][3], "AssertionError: Missing S3URI!"
                except AssertionError as e:
                    print(str(e), "\n\t", db_connect.cur.statement)
                    sys.exit(1)

                results.extend(res)
        sd = pd.DataFrame(columns=["proj_folder", "s3_loc", "fastq"])
        for row in results:
            sd = sd.append(
                [
                    {
                        "proj_folder": os.path.dirname(row[2].strip("/")),
                        "s3_loc": os.path.dirname(row[3].strip("/")),
                        "fastq": row[1],
                    }
                ]
            )

        print(tabulate(sd, headers="keys", tablefmt="fancy_grid", showindex=False))

    else:
        if any([source_path is None, target_path is None]):
            print("WARNING: Missing at least one of source_path and target_path!")
            return
        sd = pd.DataFrame(
            {"proj_folder": [source_path], "s3_loc": [target_path], "fastq": [f_in]}
        )

    sample_data = sample_data_frame(sd)

    failed_samples = []
    if not no_rsync:
        # copy fastq files, rename the samples, and update the database
        sample_set = prepare_statements(sample_data)
        for key in sample_set:
            success_list = []
            for cmd in sample_set[key]["cmd"]:
                dest_bucket_name, dest_object_name, src_data = cmd
                msg, success = put_object(
                    dest_bucket_name, dest_object_name, src_data, args["md5sums"]
                )
                if success:
                    success_list.append(success)
                else:
                    # logging.error('%s', msg.decode())
                    failed_samples.append(str(key))
            if all(success_list):
                # check if important_dates has valid IGO_sub_date and sequencing_date
                db_connect.cur.execute(
                    "SELECT IGO_sub_date, sequencing_date FROM important_dates "
                    "WHERE sampleData_id = %s",
                    (key.split("_")[0],),
                )
                res = db_connect.cur.fetchall()
                if res:
                    for i in zip(["IGO_sub_date", "sequencing_date"], res[0]):
                        if not isinstance(i[1], datetime.date):
                            stmt = (
                                "UPDATE important_dates SET {}='{}' WHERE "
                                "sampleData_id={}".format(
                                    i[0],
                                    date.fromtimestamp(os.path.getatime(src_data)),
                                    key.split("_")[0],
                                )
                            )
                            db_connect.cur.execute(stmt)
                            print(db_connect.cur.statement)
                    try:
                        db_connect.cur.execute(sample_set[key]["statement"])
                        print(db_connect.cur.statement)
                    except mysql.connector.Error as err:
                        print(
                            "Something went wrong with sample {}: {}".format(
                                key.split("_")[0], err
                            )
                        )
                        db_connect.db.rollback()
                    finally:
                        db_connect.db.commit()
                else:
                    print(
                        "No records found for sample {}:\n\t{}".format(
                            key.split("_")[0], db_connect.cur.statement
                        )
                    )
                    logging.warning(
                        "Sample '{}' will be excluded from processing!".format(
                            key.split("_")[0]
                        )
                    )
                    failed_samples.append(str(key.split("_")[0]))

    # write the processing jobs to yaml
    # need to determine `run_name` to build proper yaml files
    # don't include failed-to-transfer samples
    filter_index, exclude_index = filter_samples(sample_data)
    if exclude_index:
        logging.warning(
            "Samples {} will be excluded from processing due to missing "
            "meta data!".format(sample_data.id[exclude_index].tolist())
        )
    sample_data = sample_data.iloc[filter_index]

    criterion = sample_data["id"].map(lambda x: str(x) not in failed_samples)
    sample_data_ = sample_data[criterion]

    if sample_data_.empty:
        print("\nSample data frame is empty! Nothing to process!...\n")
        print("{:-^50}\n".format(" END "))

        return

    idx_seqc = sample_data_["run_name"].map(
        lambda x: x not in ["ATAC", "H3", "H2", "H4", "VDJ", "five_prime", "CR"]
    )
    idx_atac = sample_data_["run_name"].map(lambda x: x == "ATAC")
    idx_feature_barcoding = sample_data_["run_name"].map(
        lambda x: x in ["H3", "H2", "H4", "CiteSeq"]
    )
    idx_cellranger = sample_data_["run_name"].map(lambda x: x in ["five_prime", "CR"])
    idx_vdj = sample_data_["run_name"].map(lambda x: x == "VDJ")

    if idx_seqc.any():
        config_jobs_yml = os.path.join(args["dockerizedSEQC"], "config", args["jobs"])
        jobs_yml_config(
            sample_data_[idx_seqc],
            email=args["email"],
            ami=args["ami"],
            instance_type=args["instance_type"],
            config_jobs_yml=config_jobs_yml,
            seqcargs=args["seqcargs"],
        )

        if runseqc:
            run(execp="seqc_submit_mjobs.py", path=args["dockerizedSEQC"], **args)

    if idx_atac.any():
        if not args["tool_path"]:
            path = input("Please provide the root path to `scata`:")
            path = os.path.expanduser(path)
        else:
            path = args["tool_path"]
        config_jobs_yml = os.path.join(path, "config", args["jobs"])
        jobs_yml_config(
            sample_data_[idx_atac],
            email=args["email"],
            config_jobs_yml=config_jobs_yml,
        )

        if atac:
            run(execp="scata_submit_mjobs.py", path=path, **args)

    if idx_feature_barcoding.any():
        if not args["tool_path"]:
            path = input("Please provide the root path to `sharp`:")
            path = os.path.expanduser(path.strip())
        else:
            path = args["tool_path"]
        db_connect.cur.execute(
            "SELECT `id` FROM `tools` "
            "WHERE `tool`='{}'".format(os.path.basename(path))
        )
        try:
            tools_id = [i[0] for i in db_connect.cur.fetchall()][0]
        except IndexError:
            tools_id = input(
                "Please provide the tool `id` as it appears in the " "database:"
            )

        hsample_data = sample_data_[idx_feature_barcoding]
        inputs_labels, exclude_s = json_jobs(hsample_data, config_path=path)

        print("Excluding:", exclude_s)
        filter_excluded = sample_data_["id"].map(lambda x: str(x) not in exclude_s)
        sample_data_ = sample_data_[filter_excluded]

        if hashtag:
            # generate a secret key for cromwell server if not found in path
            secret_cromwell = get_cromwell_credentials(db_connect.config)
            print("Establishing connection to Cromwell Server, please wait ...!")
            for inputs, labels in inputs_labels:
                kargs = {
                    "inputs": inputs,
                    "labels": labels,
                    "secret": secret_cromwell,
                    "output": "Sharp.options.aws.json",
                }
                try:
                    out = run(
                        execp="./submit.sh", path=path, cromwell_param=kargs, **args
                    )
                    if out["returncode"] == 0:
                        print(inputs, labels, "successfully deployed to Cromwell!")
                    else:
                        msg = "\n" + "\n".join(
                            [
                                inputs,
                                labels,
                                "returned exit code {}".format(out["returncode"]),
                            ]
                        )

                        raise RuntimeError(msg)

                    # TODO: record output to the DB
                    label_id = os.path.basename(labels).split("_")[0]
                    igo_id = hsample_data.project_loc[
                        hsample_data.id == label_id
                    ].values[0]
                    igo_id = igo_id.lstrip("/Volumes/peerd/FASTQ/Project_").split("/")[
                        0
                    ]
                    platform = (
                        hsample_data.run_name[hsample_data.id == label_id].values[0]
                        if hsample_data.run_name[hsample_data.id == label_id].values[0]
                        == "CiteSeq"
                        else "HTO"
                    )

                    db_connect.cur.execute(
                        "INSERT INTO `raw_data` (sampleData_id, platform, IGO_id) "
                        "VALUES (%s,%s,%s)",
                        (label_id, platform, igo_id,),
                    )
                    db_connect.cur.execute("SELECT LAST_INSERT_ID()")
                    rawData_id = [i[0] for i in db_connect.cur.fetchall()]
                    rawData_id = rawData_id[0]
                    print("Update `raw_data`:\n\t", db_connect.cur.statement)

                    db_connect.cur.execute(
                        "INSERT INTO `run_records` (rawData_id,tools_id) "
                        "VALUES (%s, %s)",
                        (rawData_id, tools_id,),
                    )
                    print("Update `run_records`:\n\t", db_connect.cur.statement)
                    db_connect.cur.execute("SELECT LAST_INSERT_ID()")
                    runRecords_id = [i[0] for i in db_connect.cur.fetchall()]
                    runRecords_id = runRecords_id[0]
                    print("Update `raw_data`:\n\t", db_connect.cur.statement)

                    db_connect.cur.execute(
                        "INSERT INTO `cromwell_manager` (runRecords_id,cromwell_id) "
                        "VALUES (%s, %s)",
                        (runRecords_id, json.loads(out["stdout"])["id"],),
                    )
                    print("Update `cromwell_manager`:\n\t", db_connect.cur.statement)

                    db_connect.cur.execute(
                        "UPDATE hashtag_lib SET `status`=3 "
                        "WHERE sampleData_id={}".format(label_id)
                    )
                    print("Update `hashtag_lib`:\n\t", db_connect.cur.statement)
                except (TimeoutError, RuntimeError) as e:
                    logging.error(str(e))

    if idx_vdj.any():
        if not args["tool_path"]:
            path = input("Please provide the root path to `CellRangerVdj`:")
            path = os.path.expanduser(path)
        else:
            path = args["tool_path"]
        vdjsample_data = sample_data_[idx_vdj]
        inputs_labels, exclude_s = json_jobs(vdjsample_data, config_path=path)

        print("Excluding:", exclude_s)
        filter_excluded = sample_data_["id"].map(lambda x: str(x) not in exclude_s)
        sample_data_ = sample_data_[filter_excluded]

        if vdj:
            # generate a secret key for cromwell server if not found in path
            secret_cromwell = get_cromwell_credentials(db_connect.config)
            print("Establishing connection to Cromwell Server, please wait ...!")
            for inputs, labels in inputs_labels:
                kargs = {
                    "inputs": inputs,
                    "labels": labels,
                    "secret": secret_cromwell,
                    "output": "CellRangerVdj.options.aws.json",
                }
                try:
                    out = run(
                        execp="./submit.sh", path=path, cromwell_param=kargs, **args
                    )
                    print(inputs, labels, "successfully deployed to Cromwell!")
                    label_id = os.path.basename(labels).split("_")[0]
                    db_connect.cur.execute(
                        "UPDATE TCR_lib SET `status`=3 "
                        "WHERE sampleData_id={}".format(label_id)
                    )
                    print("Update `TCR_lib`:\n\t", db_connect.cur.statement)
                except TimeoutError as e:
                    logging.error(str(e))

    if idx_cellranger.any():
        if not args["tool_path"]:
            path = input("Please provide the root path to `sera`:")
            path = os.path.expanduser(path)
        else:
            path = args["tool_path"]
        config_jobs_yml = os.path.join(path, "config", args["jobs"])
        jobs_yml_config(
            sample_data_[idx_cellranger],
            email=args["email"],
            config_jobs_yml=config_jobs_yml,
        )

        if cr:
            run(execp="sera_submit_mjobs.py", path=path, **args)

    if save:
        print("Writing output to `{}`.".format(args["results_output"]))
        sample_data_.to_csv(args["results_output"])
    else:
        print(
            tabulate(
                sample_data_, headers="keys", tablefmt="fancy_grid", showindex=False
            )
        )

    db_connect.db.disconnect()

    return None
