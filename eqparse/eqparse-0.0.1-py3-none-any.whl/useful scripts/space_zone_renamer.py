import glob as gb
import os
import shutil



def space2zonename():

    '''
    takes all existing space names, makes new zone names according to the following naming 
	custom:

        - "Spc" > "Zn"
        - "Plnm" > "Pl Zn"
        - "[Custom Space Name]" > "[Custom Space Name] Zn"

    and makes a new input file and pd2 in a new directory in the same folder, which you can
    open and inspect. useful for renaming a bunch of spaces and keeping your space-zone
	naming integrity intact.

    '''

    directory = "Py Spc2Zn Rename"
    if os.path.exists(directory):
        shutil.rmtree(directory)

    os.makedirs(directory)

    inpfiles = gb.glob('./*.inp')
    inpfiles = [x for x in inpfiles if not '- Baseline Design' in x]
    pd2files = gb.glob('./*.pd2')

    for i in inpfiles:

        zonenames = []
        zonepos = []
        zoneassign = []
        zoneassignpos = []
        newzonenames = []

        with open(i) as f:
            f_list = f.readlines()

        for num, line in enumerate(f_list):

            if "\" = ZONE" in line:
                zonenames.append(line)
                zonepos.append(num)
            if "SPACE            = \"" in line:
                zoneassign.append(line)
                zoneassignpos.append(num)

        for num, line in enumerate(zoneassign):
            newzone = line.strip("   SPACE            = ").strip("\"").strip("\n").strip("\"")
            if "Plnm" not in newzone and "Spc" not in newzone:
                newzone = newzone + " Zn"
                newzone = "\"" + newzone + "\" = ZONE \n"
                newzonenames.append(newzone)

            else:
                newzone = newzone.replace("Plnm", "Pl Zn").replace("Spc", "Zn")
                newzone = "\"" + newzone + "\" = ZONE"
                newzonenames.append(newzone)

        flistnew = f_list

        for num, line in enumerate(zonepos):
            flistnew[line] = newzonenames[num]

        fname = "py zone swap " + i.strip('\.\\')
        if os.path.isfile(fname):
            os.remove(fname)

        with open(os.path.join(directory, fname), 'a') as output:
            for f in flistnew:
                output.write(f)

        shutil.copyfile(pd2files[0], os.path.join(directory, fname.replace('.inp', '')+'.pd2'))

if __name__ == "__main__":
    space2zonename()
    