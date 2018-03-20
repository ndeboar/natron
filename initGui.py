# CGRU init GUI script

import NatronGui
import NatronDeadline

NatronGui.natron.addMenuCommand('Deadline/Render Selected','reload(NatronDeadline);NatronDeadline.renderSelected()',QtCore.Qt.Key.Key_F10,QtCore.Qt.KeyboardModifier.NoModifier)
