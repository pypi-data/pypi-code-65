import numpy as np
import csv
from time import gmtime, strftime
import json
from scipy.spatial import distance
from vhh_sbd.Video import Video
import matplotlib.pyplot as plt
from inspect import signature
from vhh_sbd.Configuration import Configuration
import os


class Evaluation(object):
    """
    This class is used to evaluate the implemented algorithm.
    """

    def __init__(self, config_file: str):
        """
        Constructor.

        :param config_file: [required] path to configuration file (e.g. PATH_TO/config.yaml)
                                       must be with extension ".yaml"
        """
        print("create instance of evaluation ...")
        self.config_instance = Configuration(config_file)
        self.config_instance.loadConfig()

        self.precision = 0
        self.recall = 0
        self.f1score = 0


    '''
    def loadRawResultsAsCsv(self, filepath):
        # save raw results to file
        fp = open(filepath, mode='r');
        lines = fp.readlines();
        fp.close();
        # print(lines)

        dist_l = [];
        for i in range(0, len(lines)):
            line = lines[i].replace('\n', '')
            line = line.replace('[', '')
            line = line.replace(']', '')
            line = line.replace('\'', '')
            line = line.replace(',', '.')
            line = line.replace(' ', '')
            line_split = line.split(';')
            # print(line_split)
            vidname = line_split[0];
            distance = float(line_split[1]);
            dist_l.append([vidname, distance]);

        dist_np = np.array(dist_l)
        #print(dist_np.shape)
        return dist_np
    '''

    def calculateSimilarityMetric(self, results_np: np.ndarray, threshold=4.5):
        """
        This method is used to calculate the similarity metrics based on the pre-calculated raw results.

        :param results_np: This parameter must hold a valid numpy array.
        :param threshold: This parameter holds a threshold. (default: 4.5)
        :return: This method returns a numpy array including the final shot boundaries.
        """
        shot_boundaries_l = []
        for i in range(0, len(results_np)):
            vid_name = results_np[i][0]
            start = results_np[i][1]
            end = results_np[i][2]
            distances_l = results_np[i][3]
            distances_np = np.array(distances_l).astype('float')

            if(self.config_instance.activate_candidate_selection == 0):
                # just take all frame positions over specified threshold

                THRESHOLD_MODE = self.config_instance.threshold_mode
                if (THRESHOLD_MODE == "adaptive"):
                    shot_l = []
                    thresholds = []
                    window_size = self.config_instance.window_size
                    alpha = threshold
                    for i in range(0, len(distances_np)):
                        if (i % window_size == 0):
                            th = np.mean(distances_np[i:i + window_size]) * alpha
                        thresholds.append(th)
                    thresholds = np.array(thresholds)
                    print(thresholds.shape)

                    for i in range(0, len(distances_np)):
                        if (distances_np[i] > thresholds[i]):
                            idx_curr = i + 1
                            idx_prev = i
                            shot_boundaries_l.append([vid_name, idx_prev, idx_curr])
                            # print("cut at: " + str(i) + " -> " + str(i+1))
                            # print(i)
                            # print(thresholds[i])
                            # print(distances_np[i])
                if (THRESHOLD_MODE == "fixed"):
                    idx_max = np.where(distances_np > threshold)[0]
                    print(idx_max)

                    if(len(idx_max) == 1) :
                        final_idx = idx_max #+ start
                        shot_boundaries_l.append([vid_name, final_idx, final_idx + 1])
                    elif(len(idx_max) > 1):
                        final_idx = idx_max #+ start
                        print(final_idx)
                        #exit()
                        for a in range(0, len(final_idx)):
                            shot_boundaries_l.append([vid_name, final_idx[a], final_idx[a] + 1])

            elif(self.config_instance.activate_candidate_selection == 1):
                # just take all frame positions over specified threshold
                idx_max = np.argmax(distances_np)
                final_idx = idx_max + start
                shot_boundaries_l.append([vid_name, final_idx, final_idx + 1])

            # print(final_idx)

            # cv2.imwrite("./test_result" + str(i) + "_1.png", self.vid_instance.getFrame(idx_max[i]))
            # cv2.imwrite("./test_result" + str(i) + "_2.png", self.vid_instance.getFrame(idx_max[i] + 1))

        shot_boundaries_np = np.array(shot_boundaries_l)
        #print(shot_boundaries_np)
        return shot_boundaries_np

    def evaluation(self, result_np, vid_name):
        """
        This method is needed to evaluate the gathered results for a specified video.

        :param result_np: This parameter must hold a valid numpy array.
        :param vid_name: This parameter represents a video name.
        :return: This method returns the calculated TP, TN, FP and FN counters.
        """
        #print("NOT IMPLEMENTED YET");

        src_path = self.config_instance.path_videos
        gt_data = self.config_instance.path_gt_data

        if (self.config_instance.path_postfix_raw_results == 'csv'):
            vid_name = vid_name.replace('results_raw_', '')
            vid_name = vid_name.replace('.csv', '')
        elif (self.config_instance.path_postfix_raw_results == 'npy'):
            vid_name = vid_name.replace('results_raw_', '')
            vid_name = vid_name.replace('.npy', '')

        #print(vid_name)
        #vid_name = result_np[0][0];
        video_obj = Video()
        video_obj.load(src_path + "/" + str(vid_name) + ".m4v")

        # load gt
        fp = open(gt_data, 'r')
        lines = fp.readlines()
        fp.close()
        #print(lines)

        gt_l = []
        for i in range(1, len(lines)):
            line = lines[i].replace('\n', '')
            line = line.replace('[', '')
            line = line.replace(']', '')
            line = line.replace('\'', '')
            line = line.replace(',', ';')
            line = line.replace(' ', '')
            line_split = line.split(';')
            #print(line_split)
            idx = int(line_split[0])
            vidname = line_split[1]
            start = int(line_split[2])
            stop = int(line_split[3])
            gt_l.append([vidname.split('.')[0], (start, stop)])

        gt_np = np.array(gt_l)
        #print(gt_np[:10])

        '''
        # load pred
        fp = open(pred_data, 'r');
        lines = fp.readlines();
        fp.close();
        # print(lines)
        '''
        #print("AAA")
        #print(result_np)
        pred_l = []
        for i in range(0, len(result_np)):
            vidname = result_np[i][0]
            start = int(result_np[i][1])
            stop = int(result_np[i][2])
            pred_l.append([vidname, (start, stop)])

        pred_np = np.array(pred_l)
        #print(pred_np[:10])

        print(vid_name)
        idx = np.where(vid_name == pred_np)[0]
        sb_pred_np = pred_np[idx]
        #print("---------")
        #print(sb_pred_np)

        #exit()

        #print(gt_np[:10])
        idx = np.where(vid_name == gt_np)[0]
        sb_gt_np = gt_np[idx]
        #print("---------")
        #print(sb_gt_np)

        #exit()

        # video-based predictions
        tp_cnt = 0
        fp_cnt = 0
        tn_cnt = 0
        fn_cnt = 0
        for j in range(0, int(video_obj.number_of_frames)):
            curr_pos = j
            prev_pos = j - 1

            search_tuple = (prev_pos, curr_pos)
            if(len(sb_pred_np) > 0 ):
                list_pred_tmp = np.squeeze(sb_pred_np[:, 1:]).tolist()
            else:
                list_pred_tmp = []
            list_gt_tmp = np.squeeze(sb_gt_np[:, 1:]).tolist()

            gt_flag = False
            pred_flag = False

            try:
                # found tuple in pred
                res_pred = list_pred_tmp.index(search_tuple)
                #print(list_pred_tmp.index(search_tuple))
                pred_flag = True
            except:
                res_pred = 0

            try:
                # found tuple in gt
                res_gt = list_gt_tmp.index(search_tuple)
                #print(list_gt_tmp.index(search_tuple))
                gt_flag = True
            except:
                res_gt = 0

            #print(str(gt_flag) + " == " + str(pred_flag))
            tp_cond = gt_flag and pred_flag # find tuple in pred && find tuple in gt --> true
            fn_cond = gt_flag and not pred_flag # not find tuple in pred && find tuple in gt --> true
            fp_cond = not gt_flag and pred_flag
            tn_cond = not gt_flag and not pred_flag

            if(tp_cond == True):
                tp_cnt = tp_cnt + 1
            if (fp_cond == True):
                fp_cnt = fp_cnt + 1
            if (tn_cond == True):
                tn_cnt = tn_cnt + 1
            if (fn_cond == True):
                fn_cnt = fn_cnt + 1

        #precision, recall, accuracy, f1_score = self.calculateEvalMetrics(tp_cnt, fp_cnt, tn_cnt, fn_cnt);
        #tmp_str = str(vid_name) + ";" + str(tp_cnt) + ";" + str(fp_cnt) + ";" + str(tn_cnt) + ";" + str(
        #    fn_cnt) + ";" + str(precision) + ";" + str(recall) + ";" + str(accuracy) + ";" + str(f1_score)
        #print(tmp_str)
        '''
        print("---------------------------")
        print("video-based results")
        print("TP: " + str(tp_cnt))
        print("FP: " + str(fp_cnt))
        print("TN: " + str(tn_cnt))
        print("FN: " + str(fn_cnt))
        
        print("precision: " + str(precision))
        print("recall: " + str(recall))
        print("accuracy: " + str(accuracy))
        print("f1_score: " + str(f1_score))
        '''

        return tp_cnt, fp_cnt, tn_cnt, fn_cnt

    def calculateMetrics(self, tp_cnt, fp_cnt, tn_cnt, fn_cnt):
        """
        This method is used to calculate the evaluation metrics precision, recall and f1score.

        :param tp_cnt: This parameter must hold a valid integer representing the tp counter.
        :param fp_cnt: This parameter must hold a valid integer representing the fp counter.
        :param tn_cnt: This parameter must hold a valid integer representing the tn counter.
        :param fn_cnt: This parameter must hold a valid integer representing the fn counter.
        :return: This method returns the scores for precision, recall, accuracy, f1_score, tp_rate and fp_rate.
        """
        # calculate precision, recall,  accuracy
        if(tp_cnt + fp_cnt != 0):
            precision = tp_cnt / (tp_cnt + fp_cnt)
        else:
            precision = 0

        if (tp_cnt + fn_cnt != 0):
            recall = tp_cnt / (tp_cnt + fn_cnt)
        else:
            recall = 0

        if ((tp_cnt + tn_cnt + fp_cnt + fn_cnt) != 0):
            accuracy = (tp_cnt + tn_cnt) / (tp_cnt + tn_cnt + fp_cnt + fn_cnt)
        else:
            accuracy = 0

        if ((precision + recall) != 0):
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0

        if ((tp_cnt + fn_cnt) != 0):
            tp_rate = tp_cnt / (tp_cnt + fn_cnt)
        else:
            tp_rate = 0

        if ((tn_cnt + fp_cnt) != 0):
            #Specificity = True Negatives / (True Negatives + False Positives)
            fp_rate = 1 - (tn_cnt / (tn_cnt + fp_cnt))
        else:
            fp_rate = 0;

        return precision, recall, accuracy, f1_score, tp_rate, fp_rate

    def calculateEvaluationMetrics(self):
        """
        This method is used to calculate the evaluation metrics.

        :return: This methods returns a numpy array including a list of the calculated metrics (precision, recall, ...).
        """
        #print(self.config_instance.path_postfix_raw_results)
        if (self.config_instance.path_postfix_raw_results == 'csv'):
            vid_name_list = os.listdir(str(self.config_instance.path_raw_results_eval))
            vid_name_list = [i for i in vid_name_list if i.endswith('.csv')]
        elif (self.config_instance.path_postfix_raw_results == 'npy'):
            vid_name_list = os.listdir(str(self.config_instance.path_raw_results_eval))
            vid_name_list = [i for i in vid_name_list if i.endswith('.npy')]
        print(vid_name_list)

        final_results = []
        fp_video_based = None

        if(self.config_instance.threshold_mode == 'adaptive'):
            thresholds_l = [1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0,
                            3.1, 3.2, 3.3, 3.4, 3.5, 3.55, 3.6, 3.65, 3.7, 3.75, 4.0, 4.5, 5.0, 5.5, 6.0,
                            7.0, 7.5, 8.5, 9.0, 9.5, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5,
                            15.0, 15.5, 16.0
                            ]
        elif(self.config_instance.threshold_mode == 'fixed'):
            thresholds_l = [1.0, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55,
                            0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.0]
            #thresholds_l = [0.80]
        else:
            thresholds_l = []

        #print(thresholds_l)
        #exit()
        for t in thresholds_l:
        #for s in range(0, 1000):
            tp_sum = 0
            fp_sum = 0
            tn_sum = 0
            fn_sum = 0
            #THRESHOLD = s * 0.001;
            THRESHOLD = t
            #print("step: " + str(s))

            if(int(self.config_instance.save_eval_results) == 1):
                fp_video_based = open(self.config_instance.path_eval_results + "/final_results_th-" + str(THRESHOLD) + ".csv", 'w')
                header = "vid_name;tp;fp;tn;fn;p;r;acc;f1_score;tp_rate;fp_rate"
                fp_video_based.write(header + "\n")

            results_l = []
            for vid_name in vid_name_list:
                if(self.config_instance.path_postfix_raw_results == 'csv'):
                    results_np = self.loadRawResultsFromCsv(self.config_instance.path_raw_results_eval + "/" + vid_name)
                elif (self.config_instance.path_postfix_raw_results == 'npy'):
                    results_np = self.loadRawResultsFromNumpy(self.config_instance.path_raw_results_eval + "/" + vid_name)

                # calculate similarity measures of consecutive frames and threshold it
                shot_boundaries_np1 = self.calculateSimilarityMetric(results_np, threshold=THRESHOLD)
                print(shot_boundaries_np1)
                #continue

                #if (len(shot_boundaries_np1) != 0):
                tp, fp, tn, fn = self.evaluation(shot_boundaries_np1, vid_name);
                p, r, acc, f1_score, tp_rate, fp_rate = self.calculateMetrics(tp, fp, tn, fn);

                if (int(self.config_instance.save_eval_results) == 1):
                    tmp_str = str(vid_name.replace('results_raw_', '').split('.')[0]) + ";" + str(tp) + ";" + str(fp) + \
                              ";" + str(tn) + ";" + str(fn) + ";" + str(p) + ";" + str(r) + ";" + str(acc) + ";" + \
                              str(f1_score) + ";" + str(tp_rate) + ";" + str(fp_rate)
                    print(tmp_str)
                    fp_video_based.write(tmp_str + "\n")
                #else:
                #    tp = 0;
                #    fp = 0;
                #    tn = 0;
                #    fn = 0;
                #    p = 0;
                #    r = 0;
                #    acc = 0;
                #    f1_score = 0;
                results_l.append([vid_name, tp, fp, tn, fn, p, r, acc, f1_score])

                tp_sum = tp_sum + tp
                fp_sum = fp_sum + fp
                tn_sum = tn_sum + tn
                fn_sum = fn_sum + fn

            p, r, acc, f1_score, tp_rate, fp_rate = self.calculateMetrics(tp_sum, fp_sum, tn_sum, fn_sum)

            if (int(self.config_instance.save_eval_results) == 1):
                tmp_str = str("overall" + ";" + str(tp_sum) + ";" + str(fp_sum) + \
                          ";" + str(tn_sum) + ";" + str(fn_sum) + ";" + str(p) + ";" + str(r) + ";" + str(acc) + ";" + \
                          str(f1_score) + ";" + str(tp_rate) + ";" + str(fp_rate))
                print(tmp_str)

                fp_video_based.write(tmp_str + "\n")
                fp_video_based.close()

            final_results.append([str(THRESHOLD), tp_sum, fp_sum, tn_sum, fn_sum, p, r, acc, f1_score, tp_rate, fp_rate])
        final_results_np = np.array(final_results)
        return final_results_np

    def plotPRCurve(self, results_np):
        """
        This method is needed to create and plot the precision_recall curve.

        :param results_np: This parameter must hold a vaild numpy array including the precision and recall scores.
        """
        print("plot precision recall curve ... ")
        precision = np.squeeze(results_np[1:, 5:6].astype('float')).tolist()
        recall = np.squeeze(results_np[1:, 6:7].astype('float')).tolist()

        plt.figure()
        step_kwargs = ({'step': 'post'}
                       if 'step' in signature(plt.fill_between).parameters
                       else {})
        plt.step(recall, precision, color='b', alpha=0.2, where='post')
        plt.fill_between(recall, precision, alpha=0.2, color='b', **step_kwargs)

        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title("2-class Precision-Recall curve");
        plt.savefig(self.config_instance.path_eval_results + "/pr_curve.png")

    def plotROCCurve(self, results_np):
        """
        This method is needed to create and plot the roc curve.

        :param results_np: This parameter must hold a vaild numpy array including the precision and recall scores.
        """

        print("plot roc curve ... ")
        tp_rate = np.squeeze(results_np[1:, 8:9].astype('float')).tolist()
        fp_rate = np.squeeze(results_np[1:, 9:10].astype('float')).tolist()

        plt.figure()
        plt.plot(fp_rate, tp_rate, color='orange', label='ROC')
        #plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend()
        plt.savefig(self.config_instance.path_eval_results + "/roc_curve.png")

    def export2CSV(self, data_np: np.ndarray, header: str, filename: str, path: str):
        """
        This method is used to export the gathered results to a csv file.

        :param data_np: This parameter holds a valid numpy array.
        :param header: This parameter holds a csv header line (first line in the file - semicolon seperated).
        :param filename: This parameter must hold a valid file name.
        :param path: THis parameter must hold a valid file path.
        """
        # save to csv file
        fp = open(path + "/" + str(filename) + ".csv", 'w')
        fp.write(header)
        for i in range(0, len(data_np)):
            tmp_str = data_np[i][0]
            for j in range(1, len(data_np[0])):
                tmp_str = tmp_str + ";" + data_np[i][j]
                # print(str(i) + "/" + str(j) + " - " + tmp_str)
            fp.write(tmp_str + "\n")
        fp.close()

    def exportMovieResultsToCSV(self, fName, res_np):
        """
        This method is used to export video results to csv file.

        :param filepath: This parameter must hold a valid file_path.
        :param res_np: This parameter must hold a valid numpy array containing the final results.
        """
        print("start csv export ...")
        fName = fName.split('.')[0]
        print(fName)

        fp = open(str(fName) + "_movie_based.csv", mode='w')

        tmp_str = "vidname;precision;recall;f1score"
        fp.write(tmp_str + "\n")
        for i in range(0, len(res_np)):
            #print(sb_np[i])
            vidname = res_np[i][0]
            p = res_np[i][1]
            r = res_np[i][2]
            f1 = res_np[i][3]
            tmp_str = vidname + ";" + str(p) + ";" + str(r) + ";" + str(f1)
            fp.write(tmp_str + "\n")
            #csv_writer.writerow(row);

        fp.close()

    def loadResultsFromCSV(self, filepath):
        """
        This method is used to load final results from csv file.

        :param filepath: This parameter must hold a valid file_path.
        :return: This method returns a numpy array containing the final results.
        """

        print("load data from csv file ...")
        fp = open(filepath, mode='r')
        csv_reader = csv.reader(fp, delimiter=';')
        res_l = []

        for line in csv_reader:
            res_l.append(line)
        res_np = np.array(res_l)
        #print(res_np)

        fp.close()
        return res_np

    def loadRawResultsFromNumpy(self, filepath):
        """
        This method is used to load raw results from numpy array.

        :param filepath: This parameter must hold a valid file_path.
        :return: This method returns a numpy array containing the raw_results.
        """

        # save raw results to file
        print("load raw results from numpy ...")
        vid_name = filepath.split('/')[-1].split('.')[0]
        raw_results = np.load(filepath, allow_pickle=True)

        start = raw_results[0][0]
        stop = raw_results[0][1]
        dist_l = raw_results[0][2]
        dist_np = np.array(dist_l).astype('float')

        array_list = []
        array_list.append([vid_name.replace("results_raw_", ""), start, stop, dist_np])
        array_np = np.array(array_list)
        return array_np;

    def loadRawResultsFromCsv(self, filepath):
        """
        This method is used to load raw results from csv file.

        :param filepath: This parameter must hold a valid file_path.
        :return: This method returns a numpy array containing the raw_results.
        """
        # save raw results to file
        fp = open(filepath, mode='r')
        lines = fp.readlines()
        fp.close()
        #print(len(lines))

        final_l = []
        for i in range(0, len(lines)):
            line = lines[i].replace('\n', '')
            line = line.replace('[', '')
            line = line.replace(']', '')
            line = line.replace(')', '')
            line = line.replace('(', '')
            #line = line.replace('list', '')
            line = line.replace('\'', '')
            line = line.replace(',', '.')
            #line = line.replace(' ', '')
            line_split = line.split(';')
            vidname = line_split[0]
            start = int(line_split[1])
            end = int(line_split[2])
            dist_l = line_split[3:]
            dist_np = np.array(dist_l).astype('float')
            final_l.append([vidname, start, end, dist_np])

        final_np = np.array(final_l)
        return final_np

    def run(self):
        """
        This method is needed to run the evaluation process.
        """
        print("evaluation ... ")

        final_results_np = self.calculateEvaluationMetrics()
        print(final_results_np)
        self.plotPRCurve(final_results_np)
        self.plotROCCurve(final_results_np)

        '''
        # export results to csv file
        self.export2CSV(final_results_np,
                                     "threshold;p;r;acc;f1_score" + "\n",
                                     "final_evaluation_pr_curve",
                                     "../Develop/");
        '''