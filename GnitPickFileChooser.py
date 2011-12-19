import java.awt
import java.awt.event
import java.awt.FlowLayout as FlowLayout

import java.io

import javax.swing
import javax.swing.JFileChooser as JFileChooser
import javax.swing.JFrame as JFrame
import javax.swing.JLabel as JLabel
import javax.swing.JButton as JButton
import java.awt.event.ActionListener as ActionListener
import java.awt.event.WindowAdapter as WindowAdapter

#from ThumbNailFileView import ThumbNailFileView
#from ThumbNailFileView import Icon16
#from BasicWindowMonitor import BasicWindowMonitor


#self.buttonlistener = ButtonMonitor(self)
#self.openButton.addActionListener( self.buttonlistener )

class GnitPickFileChooser(ActionListener):
  def __init__(self,frm):
    self.frame = frm

  def actionPerformed(self,e):
      self.chooser = JFileChooser()
      self.option = self.chooser.showOpenDialog(self.frame)
      
      if (self.option == JFileChooser.APPROVE_OPTION):
          self.frame.statusbar.setText("You chose " + self.chooser.getSelectedFile().getName())
      else:
          self.frame.statusbar.setText("You cancelled.")

   # Stand-alone Unit Execution
if __name__ == "__main__":
   vc = MyViewChooser()
   vc.setVisible( 1 )

 