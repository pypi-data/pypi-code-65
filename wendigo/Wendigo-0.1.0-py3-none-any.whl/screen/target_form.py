from wendigo.core import Area
from wendigo.screen.dll import TargetForm as DllTargetForm
from wendigo.system import Rectangle

class TargetForm:
    """
    Target form.
    """
    def __init__(self, target_form: DllTargetForm):
        """
        Initialize.
        """
        self.target_form = target_form

    @property
    def area(self) -> Area:
        """
        Get area.

        Returns
        -------
        area: Area.
        """
        area = self.target_form.Area
        return Area(area.X, area.Y, area.Width, area.Height)
        
    @area.setter
    def area(self, area: Area):
        """
        Set area.

        Parameters
        ----------
        area: Area.
        """
        self.target_form.Area = Rectangle(area.x, area.y, area.width, area.height)

    def close(self):
        """
        Close the target form.
        """
        self.target_form.Close()
        self.target_form.Dispose()