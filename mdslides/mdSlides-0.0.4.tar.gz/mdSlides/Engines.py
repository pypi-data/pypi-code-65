import subprocess, pathlib, os, shutil, urllib
from . import Utils

def is_exe(path):
  if path.is_file():
    if os.access(str(path),os.X_OK):
      return True
  return False

class Engine:
  '''
  A base class that implements common code for all engines. To add a new engine, one just needs to derive
  from this class 
  '''

  def __init__(self, preprocess_script_name=None, postprocess_script_name=None):

    self.preprocess_script = self.make_path("preprocess" if preprocess_script_name is None else preprocess_script_name)
    self.postprocess_script = self.make_path("postprocess" if postprocess_script_name is None else postprocess_script_name)

  def preprocess(self,input):
    if is_exe(self.preprocess_script):
      input_dir = input.parent
      processed_input = input_dir/f"{str(input.stem)}-process.md"

      print(f"Pre-processing: {input} -> {processed_input}")

      cmd = ["./"+str(self.preprocess_script),str(input),str(processed_input)]
      self.run_cmd(cmd)

      return processed_input
    
    return input

  def postprocess(self,output):
    if is_exe(self.postprocess_script):
      output_dir = output.parent

      print(f"Post-processing: {output}")

      cmd = ["./"+str(self.postprocess_script),str(output)]
      self.run_cmd(cmd)

  def build(self,input,output=None):
    '''Builds a presentation from an input markdown file. First calls .preprocess(...) method,
    then ._build(...) method (which should be impemented by derived class, aad finally calls
    .postprocess(...) method.
    '''
    input = self.make_path(input)
    if output is None:
      output_dir = self.setup_output_dir(input,output)
      output = output_dir/self._get_default_output_filename(input)

    input = self.preprocess(input)
    print(f"Generating slides: {input} -> {output}")
    output = self._build(input,output)
    self.postprocess(output)

  def make_path(self,file):
    return pathlib.Path(file)

  def setup_output_dir(self,input_path,output_path):
    '''
    Setup the output directory for a slideshow, creating
    it if it does not exist.
    .
    If output is None, it will be computed from input.
    '''

    if output_path is None:
      output_path = input_path.parent/input_path.stem

    if not output_path.exists():
      output_path.mkdir()

    return output_path

  def run_cmd(self,cmd,desc=None,verbose=0):
   if desc is None:
     desc = "running:" + " ".join(cmd)
   else:
     if verbose > 0:
       print(desc)

   result = subprocess.run(cmd, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   if result.returncode != 0:
     print(f"There was an error {desc}")
     print(result.stdout.decode('utf-8'))

  def get_sources_from_html(self,file):
    if not isinstance(file,pathlib.Path):
      file = pathlib.Path(file)

    parser = Utils.TagWithSourceParser()
    parser.feed( file.read_text() )
    return parser.sources

  def copy_sources_to_output(self,output_path):
    sources = self.get_sources_from_html(output_path)
    for source in sources:
      # don't copy urls
      if urllib.parse.urlparse(str(source)).scheme != "":
        continue
      # don't copy absolute paths
      if source.is_absolute():
        continue

      if not source.exists():
        continue

      print(f"copying {str(source)} to {str(output_path.parent)}")
      os.makedirs(output_path.parent/source.parent, exist_ok=True)
      shutil.copyfile(source,output_path.parent/source.parent/source.name)
      




class PandocSlidy(Engine):

  def _get_default_output_filename(self,input):
    '''return default path to output file for a given input file.'''
    return "index.html"

  def _build(self,input,output):

    output_dir = output.parent

    if not (output_dir/"data").exists():
      super().run_cmd(['git','clone', 'https://github.com/slideshow-templates/slideshow-slidy.git',str(output.parent/"data")],"fetching slidy data files")
      shutil.rmtree(str(output.parent/"data/.git"))


    # pandoc options:
    # --self-contained does not work with mathjax
    # --standalone creates a file with header and footer
    # --mathjax uses mathjax javascript to render latex equation. requires an internet connection
    # --to is the format that will be written to
    cmd = list()
    cmd.append("pandoc")
    cmd.append(str(input))
    cmd.append("-o")
    cmd.append(str(output))
    cmd.append("--standalone")
    cmd.append("--mathjax")
    cmd.append("--to")
    cmd.append("slidy")
    cmd.append("--css")
    cmd.append("slidy_extra.css")
    cmd.append("--variable")
    cmd.append("slidy-url=./data")

    super().run_cmd(cmd,"building the slides.")

    super().copy_sources_to_output(output)

    return output


  
class PandocPowerPoint(Engine):

  def _get_default_output_filename(self,input):
    '''return default path to output file for a given input file.'''
    return str(input.stem)+".pptx"

  def _build(self,input,output):
    template_file = pathlib.Path("mdSlides-template.pptx")

    cmd = list()
    cmd.append("pandoc")
    cmd.append(str(input))
    cmd.append("-o")
    cmd.append(str(output))
    if template_file.exists():
      cmd.append("--reference-doc")
      cmd.append(str(template_file))

    super().run_cmd(cmd,"building the slides.")

    return output
