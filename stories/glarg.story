<?xml version="1.0"?>
<story id="itemLabelKeptCurrent" title="Item Pane Labels Kept Current">
   <text>The item pane label is kept current relative to the state the item was in when it was most recently saved to or retrieved from persistent storage.</text>

   <history timestamp="7-5-2005 2:00pm EST">Authored by mca</history>

   <task>When item is loaded, use its "story/@id" as the label.</task>
   <task>When an item is saved, replace its label with the value of its "story/@id".</task>
</story>
