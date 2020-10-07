# Created by Tiago Sanches da Silva: tiago.eem@gmail.com :)
import os

colab = True

try:
    import sys
    from IPython import get_ipython

    if not('google.colab' in str(get_ipython())):
        print('This script was made to run only on Google Colab notebooks, other environments was not tested completely')
        colab = False
        #sys.exit()      
except:
    print('This script was made to run only on Google Colab notebooks, other environments was not tested completely')
    colab = False
    #sys.exit()

def compareVersion( version1, version2):
    versions1 = [int(v) for v in version1.split(".")]
    versions2 = [int(v) for v in version2.split(".")]
    for i in range(max(len(versions1),len(versions2))):
        v1 = versions1[i] if i < len(versions1) else 0
        v2 = versions2[i] if i < len(versions2) else 0
        if v1 > v2:
            return 1
        elif v1 <v2:
            return -1
    return 0
# To check a version of plotly without import, to be able to upgrade without restart
# Try to import Plotly (should be alreay instaled, but...)
#import plotly (don't use here)

version = '0.0.0'

if (colab == True):

    try:
        os.system('pip freeze | grep plotly > plotly.version')
        f = open("plotly.version", "r")
        if f.mode == 'r':
            version_file = f.readline()

        version = version_file[:-1].split('==')[1]
        f.close()
        os.system('rm plotly.version')
    except:
        print('pip install plotly==4.10.0')
        os.system('pip install plotly==4.10.0')

    # Check version of plotly, if is greater than 4.9 gitly will use kaleido, if not will use urca
    if ( compareVersion( version,  '4.9.0') > 0 ):
        os.system('pip install -U kaleido')
    else:
        print('Plotly version fewer than 4.9.0, orca module will be necessary')
        print('Summary: Install Orca, update plotly and update apt-get')
        print('')
        print('apt-get update')
        os.system('apt-get update')
        print('pip install plotly==4.8.1')
        os.system('pip install plotly==4.8.1')
        print('wget https://github.com/plotly/orca/releases/download/v1.2.1/orca-1.2.1-x86_64.AppImage -O /usr/local/bin/orca')
        os.system('wget https://github.com/plotly/orca/releases/download/v1.2.1/orca-1.2.1-x86_64.AppImage -O /usr/local/bin/orca')
        print('chmod +x /usr/local/bin/orca')
        os.system('chmod +x /usr/local/bin/orca')
        print('apt-get install xvfb libgtk2.0-0 libgconf-2-4')
        os.system('apt-get install xvfb libgtk2.0-0 libgconf-2-4')
    else:
        print('You are not in Colab envirement, make sure you already have Plotly > 4.9.0 and kaleido')
   


class GitlyPlotter:

    static = True
    default_H = 450
    default_W = 800
    default_S = 1
    use_kaleido = True

    def __init__ (self, renderer = 'git', default_height = 450, default_width = 800, default_scale = 1):

        if (renderer.lower() == 'git') or (renderer.lower() == 'github'):
            self.static = True
        else:
            self.static = False

            self.default_H = default_height
            self.default_W = default_width
            self.default_S = default_scale

        import plotly
        if (compareVersion( plotly.__version__,  '4.9.0') <= 0 ):
            self.use_kaleido = False
        else:
            self.use_kaleido = True


    def config_render(self, renderer = 'colab', default_height = None, default_width = None, default_scale = None):
        if (renderer == 'colab'):
            self.static = False
        else:
            self.static = True

        if not(default_height == None):
            self.default_H = default_height
        if not(default_width == None):
            self.default_W = default_width
        if not(default_scale == None):
            self.default_S = default_scale


    def show(self, figure = None, **kwargs ):
        from IPython.display import Image, HTML, display

        if figure == None :
            return display(HTML('<h1>Where is my figure?</h1><br><p>You should pass me the figure from plotly, like: gitly.show( fig )<br>Check this easy example: https://github.com/Tiagoeem/gitly/blob/master/examples/Using_Gitly_Example.ipynb'))

        #try:
        if self.static:
            if 'width' in kwargs:
                w = kwargs.get("width")
            else: 
                w = self.default_W

            if 'height' in kwargs:
                h = kwargs.get("height")
            else: 
                h = self.default_H

            if 'scale' in kwargs:
                s = kwargs.get("scale")
            else: 
                s = self.default_S

            if 'format' in kwargs:
                f = kwargs.get("format")
            else: 
                f = 'png'

            if ( self.use_kaleido == True ):
                img_bytes = figure.to_image(format=f, height=max(h,250), width=max(w,250), scale=s, engine='kaleido')
            else:
                img_bytes = figure.to_image(format=f, height=max(h,250), width=max(w,250), scale=s)
    
            return Image(img_bytes)
        else:
            return figure.show()

        #except:
        #    print('Error: Are you sure that you send me a valid plotly figure?')
        #    print('Please refer: https://github.com/Tiagoeem/gitly')
