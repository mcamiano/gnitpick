"""LineHighlightPainter.py
   transliterated from O'Reilly's Java Swing 
   LineHighlightPainter.java
   By Mitch Amiano
   Agile Markup Corporation
"""

from java.awt import *
from javax.swing import *
from javax.swing.text import *
from javax.swing.plaf import TextUI

# A sample HighlightPainter implementation that underlines highlighted text with
# a thick line.
class LineHighlightPainter( Highlighter.HighlightPainter ):

  # Create a new painter using the given color
   def __init__(self, c):
    #"@sig public LineHighlightPainter(Color c)"
    self.color = c 

   def getColor(self):
    #"@sig public Color getColor()"
    return self.color 

   # Paint a bunch of little rectangles
   def paint( self, g,  p0, p1, bounds, c) :
    #"@sig public void paint(Graphics g, int p0, int p1, Shape bounds, JTextComponent c)"

    try :
      # Convert positions to pixel coordinates
      ui = c.getUI()

      r1 = ui.modelToView(c, p0)
      r2 = ui.modelToView(c, p1)
      b = bounds.getBounds()
      
      x1 = r1.x
      x2 = r2.x
      y1 = r1.y
      y2 = r2.y
      y1base = y1 # start rect here
      y2base = y2 # start rect here

      # Start painting
      g.setColor( self.getColor() )

      # Special case if points are on the same line
      if (y1 == y2):
        g.fillRoundRect(x1, y1base, x2 - x1, r1.height, r1.height/3, r1.height/2 )

      else:
        # Fill from point 1 to the end of the line
        g.fillRoundRect(x1, y1base, b.x+b.width-x1, r1.height, r1.height/3, r1.height/2 )

        # Fill all the full lines in between (assumes that
        # all lines are the same height . . . not a good assumption
        # if using a JEditorPane/JTextPane)
        line = y1base + 1 + r1.height        
        while (line < y2):
          g.fillRect(b.x, line-1, b.width, r1.height )
          line += r1.height

        # Last line . . . from the beginning to point 2
        g.fillRoundRect(b.x, y2base, x2 - b.x, r1.height, r1.height/3, r1.height/2 )

    except BadLocationException, ex: # Can't paint
      pass

   def  LHCaret(self):
       return LHCaret()
        
import sys
  # A Caret that uses LineHighlightPainter
class LHCaret(DefaultCaret):
    def __init__(self):
        pass
    def getSelectionPainter(self):
        return LineHighlightPainter( self.getComponent().getSelectionColor() ) 