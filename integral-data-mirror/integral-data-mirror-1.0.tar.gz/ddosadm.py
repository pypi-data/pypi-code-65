import ddosa
import datamirror
import glob
import os
import gzip
import subprocess

class DataSourceConfig(ddosa.DataAnalysis):
    store_files=True

class AUXADP(ddosa.DataAnalysis):
    input_rev=ddosa.RevForScW

    def main(self):
        print self.input_rev.auxadppath
        print self.input_rev.revdir
        # this is fetched at the same time as scw, should be not


class ScWData(ddosa.ScWData):
    cached=True
    test_files=False
    rename_output_unique=False
    #datafile_restore_mode="url_in_object"

    version="v3aux"

    input_datasourceconfig=DataSourceConfig

    @property
    def integral_data(self):
        return os.environ.get('INTEGRAL_DATA','/isdc/arc/rev_3/')

    def check_aux_adp_ref(self):
        if not os.path.exists(self.integral_data+"/aux/adp/ref/"):
            return False

        return True
            
    def update_aux_adp_ref(self):
        print("updating AUX ADP REF...")
        subprocess.check_call(["rsync","-Lzrtv","isdcarc.unige.ch::arc/FTP/arc_distr/NRT/public/aux/adp/ref/",self.integral_data+"/aux/adp/ref"])

    def main(self):
        try:
            ddosa.ScWData.main(self)
        except ddosa.dataanalysis.AnalysisException as e:
            print "offline ScWData failed:",e
            datamirror.ensure_data(scw=self.input_scwid.str(),kind="any")
            ddosa.ScWData.main(self)

        self.scwfilelist=[]

        if not self.check_aux_adp_ref():
            print("updating aux adp ref")
            self.update_aux_adp_ref()
            

        if self.input_datasourceconfig.store_files:
            print "searching for ScW files:",self.scwpath+"/*"
            targz="scw_pack.tar"
            subprocess.check_call(["tar","-C",self.scwpath,"-cvf",targz,"."])
            self.scwpack=ddosa.DataFile(targz)

            scwid=self.input_scwid.str()
            rev=scwid[:4]

            auxadproot=self.integral_data+"/aux/adp/"
            auxadpfn=auxadproot+rev+"_auxadpdir.tgz"

            if not os.path.exists(auxadpfn):
                auxadpfn=rev+"_auxadpdir.tgz"
                subprocess.check_call(["tar","-C",auxadproot,"-cvf",auxadpfn,rev+".001"])

            self.auxadppack=ddosa.DataFile(auxadpfn)

            

    def post_restore(self):
        if self.input_datasourceconfig.store_files:
            scwid=self.input_scwid.str()
            rev=scwid[:4]
            self.scwpath=self.integral_data+"/scw/"+rev+"/"+scwid
            self.swgpath=self.scwpath+"/swg.fits"
            
            if not os.path.exists(self.scwpath): os.makedirs(self.scwpath)
            cmd=["tar","-C",self.scwpath,"-xvf",os.path.abspath(self.scwpack.get_path())]
            print "cmd",cmd
            subprocess.check_call(cmd)
            print "restored scw in",self.scwpath
            
            auxadppath=self.integral_data+"/aux/adp"
            if not os.path.exists(auxadppath): os.makedirs(auxadppath)
            cmd=["tar","-C",auxadppath,"-xvf",os.path.abspath(self.auxadppack.get_path())]
            print "cmd",cmd

            try:
                subprocess.check_call(cmd)
            except:
                print "failed!"
            print "restored aux in",self.auxadppath

class ICRoot(ddosa.DataAnalysis):
    input="standard_IC"

    cached=False # level!

    schema_hidden=True
    version="v1"
        
    def validate_ic(self):
        if not os.path.exists(self.icroot+"/idx/ic_master_file.fits"):
            return False

        return True
            
    def update_ic(self):
        print("updating IC...")
        subprocess.check_call(["rsync","-Lzrtv","isdcarc.unige.ch::arc/FTP/arc_distr/ic_tree/prod/ic/",self.icroot+"/ic/"])
        subprocess.check_call(["rsync","-Lzrtv","isdcarc.unige.ch::arc/FTP/arc_distr/ic_tree/prod/idx/",self.icroot+"/idx/"])

    def main(self):
        self.icroot=os.environ.get('CURRENT_IC','/data/ic_tree_current')

        if not self.validate_ic():
            print("no IC found!")
        
            self.update_ic()
            

        self.icindex=self.icroot+"/idx/ic/ic_master_file.fits[1]"

        print('current IC:',self.icroot)


class IBIS_ICRoot(ddosa.DataAnalysis):
    input_icroot=ICRoot
    
    cached=False # level!

    def main(self):
        self.ibisicroot=self.input_icroot.icroot+"/ic/ibis"
        print("current IBIS ic root is:"),self.ibisicroot


class GRcat(ddosa.DataAnalysis):
    cached=False # again, this is transient-level cache

    refcat_version=41

    def get_version(self):
        return self.get_signature()+"."+self.version+".%i"%self.refcat_version

    def check(self):
        if os.path.exists(self.cat):
            return True
        return False

    def update(self):
        subprocess.check_call(["wget","https://www.isdc.unige.ch/integral/download/osa/cat/osa_cat-41.0.tar.gz","-O","/data/resources/osa_cat-41.0.tar.gz"])
        subprocess.check_call(["tar","xvzf","osa_cat-41.0.tar.gz"],cwd="/data/resources/")

    def main(self):
        self.cat="/data/resources/osa_cat-{0:d}.0/cat/hec/gnrl_refr_cat_{0:04d}.fits".format(self.refcat_version)
        print("searching for local cat as",self.cat)

        if not self.check():
            print("no catalog here")
            self.update()
            if not self.check():
                raise RuntimeError("failed update properly!")
    

