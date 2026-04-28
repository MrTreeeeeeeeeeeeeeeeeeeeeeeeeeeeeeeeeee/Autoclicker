; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Paused := 1
Loop
  ;Read
  {
      FileRead, MillisPerClick, .\settings\settings1.txt
      FileRead, RandomClickTimeMin, .\settings\settings2.txt
      FileRead, RandomClickTimeMax, .\settings\settings3.txt
      FileRead, LangthOfClick, .\settings\settings4.txt
      FileRead, StartStopHotkey, .\settings\settings5.txt
      FileRead, OpenMenu, .\settings\settings6.txt
      Break
}

Gui, Add, Text, x12 y12 w140 h20 +Left, Time Between Clicks In Mill
Gui, Add, Edit, x162 y9 w70 h20 +Number vMillisPerClick, %MillisPerClick%
Gui, Add, Text, x12 y52 w90 h20 +Left, Add Random Min
Gui, Add, Edit, x112 y49 w70 h20 +Number vRandomClickTimeMin, %RandomClickTimeMin%
Gui, Add, Text, x202 y52 w90 h20 +Left, Add Random Max
Gui, Add, Edit, x302 y49 w70 h20 +Number vRandomClickTimeMax, %RandomClickTimeMax%
Gui, Add, Text, x12 y92 w90 h20 +Left, Langth Of Click
Gui, Add, Edit, x112 y89 w70 h20 +Number vLangthOfClick, %LangthOfClick%
Gui, Add, Text, x12 y132 w60 h20 +Left, Start/Stop
Gui, Add, Hotkey, x82 y129 w90 h20 vStartStopHotkey, %StartStopHotkey%
Gui, Add, Button, x12 y209 w60 h30 +Center, Save
Gui, Add, Text, x12 y172 w80 h20 +Left, Show Menu
Gui, Add, Hotkey, x102 y169 w90 h20 vOpenMenu, %OpenMenu%
; Generated using SmartGUI Creator 4.0
Gui, Show, x503 y457 h250 w400, AutoClicer
Return

GuiClose:
ExitApp

ButtonSave:
If (TimesSaved > 0)
   {
      Hotkey,%StartStopHotKey%, StartStopHotkeyEnd, Off
      Hotkey,%OpenMenu%, OpenMenuEnd, Off
   }
Gui, Submit, Nohide
Gui, Destroy
TimesSaved++
Hotkey,%StartStopHotKey%, StartStopHotkeyEnd
Hotkey,%OpenMenu%, OpenMenuEnd
Loop
  ;Write
  {
      
      FileDelete, .\settings\settings1.txt
      FileAppend, %MillisPerClick%, .\settings\settings1.txt
      FileRead, MillisPerClick, .\settings\settings1.txt

      FileDelete, .\settings\settings2.txt
      FileAppend, %RandomClickTimeMin%, .\settings\settings2.txt
      FileRead, RandomClickTimeMin, .\settings\settings2.txt

      FileDelete, .\settings\settings3.txt
      FileAppend, %RandomClickTimeMax%, .\settings\settings3.txt
      FileRead, RandomClickTimeMax, .\settings\settings3.txt

      FileDelete, .\settings\settings4.txt
      FileAppend, %LangthOfClick%, .\settings\settings4.txt
      FileRead, LangthOfClick, .\settings\settings4.txt

      FileDelete, .\settings\settings5.txt
      FileAppend, %StartStopHotkey%, .\settings\settings5.txt
      FileRead, StartStopHotkey, .\settings\settings5.txt

      FileDelete, .\settings\settings6.txt
      FileAppend, %OpenMenu%, .\settings\settings6.txt
      FileRead, OpenMenu, .\settings\settings6.txt

      Break
}



Loop, {
      If (Paused = 0)
      {
       Random, RandomClickTIme, %RandomClickTimeMin%, %RandomClickTimeMax%
       Click, Left, , , , , Down
       Sleep, %LangthOfClick%
       Click, Left, , , , , Up
       Sleep %MillisPerClickEnd%
         MillisPerClickEnd = %MillisPerClick%
         MillisPerClickEnd += %RandomClickTIme%
       }
}

 StartStopHotkeyEnd:
   MillisPerClickEnd = 0
   LangthOfClick = 0
     If (Paused = 0) {
       Paused = 1
     }
     Else {
     Paused = 0
     }
Return

OpenMenuEnd:
Reload
Return
