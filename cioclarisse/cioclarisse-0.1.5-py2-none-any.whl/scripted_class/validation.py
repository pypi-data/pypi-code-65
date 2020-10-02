# import abc
# import importlib
# import inspect
import os
import ix

from ciocore.gpath import Path
from ciocore.gpath_list import GLOBBABLE_REGEX, PathList
from ciocore.validator import Validator, ValidationError
from cioclarisse import const as k
from ciocore import data as coredata
from cioclarisse.scripted_class import frames_ui 
from cioclarisse.scripted_class import dependencies as deps
from cioclarisse.scripted_class import validation_ui

from ciocore.sequence import Sequence
 
class ValidateImagesAndLayers(Validator):
    def run(self, _):
 
        images = ix.api.OfObjectArray()
        self._submitter.get_attribute("images_and_layers").get_values(images)
        out_paths = PathList()

        num_images = images.get_count()

        if not num_images:
            msg = "No render outputs added. Please add images and/or layers in the Submitter"
            self.add_error(msg)
            return

        for image in images:
            if not image.get_attribute("render_to_disk").get_bool():
                msg = "Image or Layer does not have render_to_disk attribute set: {}".format(image.get_full_name())
                self.add_error(msg)
                continue
            

            save_path = image.get_attribute("save_as").get_string()
            if not save_path:
                msg = "Image save_as path is not set: {}".format(image.get_full_name())
                self.add_error(msg)
                continue
    
            if save_path.endswith("/"):
                msg =  "Image save_as path must be a filename, not a directory: {}".format( image.get_full_name() )
                self.add_error(msg)
                continue
    

            directory = os.path.dirname(save_path)
            out_paths.add(directory)

        if not out_paths:
            msg = "There are no images or layers with Save to Disk turned on."
            self.add_error(msg)
            return
    
        common_path = out_paths.common_path()

        paths = "\n".join(p.posix_path() for p in out_paths)

        if common_path.depth == 0:
            msg = "Your output files should be rendered to a common folder. {}\n{}".format(common_path.posix_path(), paths )
            self.add_error(msg)
            return

        if self._submitter.get_attribute("use_custom_frames").get_bool():
            frame_seq = frames_ui.custom_frame_sequence(self._submitter)
            if not frame_seq:
                self.add_error("Error validating custom frames sequence.")
            for image in images:
                image_rng = frames_ui.image_range(image)
                image_seq = Sequence.create(*image_rng)
                isect = image_seq.intersection(frame_seq)
                if list(isect) != list(frame_seq):
                    self.add_warning("Image has less frames than custom sequence. {}".format( image.get_full_name()))


class ValidateTaskCount(Validator):
    def run(self, _): 
        seq = frames_ui.main_frame_sequence(self._submitter)
        if not seq:
            self.add_error("No valid frame seqence. Either ensure connected images have a valid sequence, or overide the fame range in the subitter.")
            return
        count = seq.chunk_count()
        if  count > 1000:
            self.add_notice(
                "This submission contains over 1000 tasks ({}). Are you sure this is correct?".format(count))

class ValidatePackages(Validator):
    def run(self, _):
 
        if not (
            self._submitter.get_attribute("clarisse_version")
            .get_applied_preset_label()
            .startswith("clarisse")
        ):
            self.add_error("No Clarisse package selected.")

class ValidateProject(Validator):
    def run(self, _): 
        projects = coredata.data().get("projects")

        project_att = self._submitter.get_attribute("conductor_project_name")
        label = project_att.get_applied_preset_label()
        if not label or label == k.NOT_CONNECTED :
            msg = 'Project is not set for "{}".'.format(self._submitter.get_name())
            self.add_error(msg)
        try:
            next(p for p in projects if str(p) == label)
        except StopIteration:
            msg = 'Cannot find project "{}" at Conductor. Please ensure the PROJECT dropdown contains a valid project.'.format(label)
            self.add_error(msg)
 
class ValidateUploadDaemon(Validator):
    def run(self, _): 
        print "ValidateUploadDaemon" 
        use_daemon = not self._submitter.get_attribute("local_upload").get_bool()
        print "use_daemon" , use_daemon
        if not use_daemon:
            return

        msg  = "This submission expects an uploader daemon to be running"
        print "add_notice" , msg
        self.add_notice(msg)


  
class ValidateMissingAssets(Validator):

    def run(self, _):
 
        basenames =  deps.CONDUCTOR_SCRIPTS + [deps.CLARISSE_CFG_FILENAME]

        path_list = PathList()

        for gpath in deps.collect(self._submitter, do_glob=False):

            # we can assunme that all globbable paths, (those containing glob
            # characters) cannot possibly represent missing files because they are
            # literally resolved  by checking what matches on disk. Therfore, we ignore them.
            if not GLOBBABLE_REGEX.search(gpath.posix_path()):
                path_list.add(gpath)

        # path_list has taken care of deduplication by now - yay
        missing = []
        for gpath in path_list:
            pp = gpath.posix_path()
            if any(pp.endswith(x) for x in basenames):
                continue
            if not os.path.exists(pp):
                missing.append(pp)

        if missing:
            for asset in missing:
                self.add_warning("Missing: {}".format(asset))

def run(node, dry_run=False):
 
    errors, warnings, notices = _run_validators(node)

    if errors:
        for error in errors:
            ix.log_error(error)
        msg = "There are some critical issues. You can't submit until you fix them."
        raise ValidationError(msg)

    if notices or warnings:
        dialog_result = validation_ui.proceed(warnings,notices,dry_run)
        
        if not dialog_result:
            msg = "Submission cancelled by user."
            raise ValidationError(msg)
    else:
        ix.log_info("There are no Notices or Warnings")

 
def _run_validators(node):
    validators =  [plugin(node) for plugin in Validator.plugins()]
    for validator in validators:
        validator.run("main")

    errors = list(set.union(*[validator.errors for validator in validators]))
    warnings = list(
        set.union(*[validator.warnings for validator in validators]))
    notices = list(set.union(*[validator.notices for validator in validators]))
    return errors, warnings, notices
