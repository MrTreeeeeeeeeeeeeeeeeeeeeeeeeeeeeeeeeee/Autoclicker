#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Paused = 1
OutputDebug,  AutoClicer is now paused
Loop
  ;Read
  {
      FileRead, MillisPerClick, .\settings\settings1.txt
      OutputDebug, 1= %MillisPerClick%
      FileRead, RandomClickTimeMin, .\settings\settings2.txt
      OutputDebug, 2= %RandomClickTimeMin%
      FileRead, RandomClickTimeMax, .\settings\settings3.txt
      OutputDebug, 3= %RandomClickTimeMax%
      FileRead, LangthOfClick, .\settings\settings4.txt
      OutputDebug, 4= %LangthOfClick%
      FileRead, StartStopHotkey, .\settings\settings5.txt
      OutputDebug, 5= %StartStopHotkey%
      FileRead, OpenMenu, .\settings\settings6.txt
      OutputDebug, 6= %OpenMenu%
      Break
}

OutputDebug, Opened Menu Start
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
OutputDebug, Opened Menu End
Return

GuiClose:
OutputDebug, Goodbye
ExitApp

ButtonSave:
If (TimesSaved > 0)
   {
      OutputDebug, %StartStopHotkey%
      Hotkey,%StartStopHotKey%, StartStopHotkeyEnd, Off
      Hotkey,%OpenMenu%, OpenMenuEnd, Off
   }
Gui, Submit, Nohide
Gui, Destroy
TimesSaved++
OutputDebug, Destroyed Menu
Hotkey,%StartStopHotKey%, StartStopHotkeyEnd
Hotkey,%OpenMenu%, OpenMenuEnd
OutputDebug, MillisPerClick = %MillisPerClick%
OutputDebug, RandomClickTimeMin = %RandomClickTimeMin%
OutputDebug, RandomClickTimeMax = %RandomClickTimeMax%
OutputDebug, LangthOfClick = %LangthOfClick%
OutputDebug, StartStopHotkey = %StartStopHotkey%
OutputDebug, OpenMenu = %OpenMenu%
Loop
  ;Write
  {
      
      FileDelete, .\settings\settings1.txt
      FileAppend, %MillisPerClick%, .\settings\settings1.txt
      FileRead, MillisPerClick, .\settings\settings1.txt
      OutputDebug, 1= %MillisPerClick%

      FileDelete, .\settings\settings2.txt
      FileAppend, %RandomClickTimeMin%, .\settings\settings2.txt
      FileRead, RandomClickTimeMin, .\settings\settings2.txt
      OutputDebug, 2= %RandomClickTimeMin%

      FileDelete, .\settings\settings3.txt
      FileAppend, %RandomClickTimeMax%, .\settings\settings3.txt
      FileRead, RandomClickTimeMax, .\settings\settings3.txt
      OutputDebug, 3= %RandomClickTimeMax%

      FileDelete, .\settings\settings4.txt
      FileAppend, %LangthOfClick%, .\settings\settings4.txt
      FileRead, LangthOfClick, .\settings\settings4.txt
      OutputDebug, 4= %LangthOfClick%

      FileDelete, .\settings\settings5.txt
      FileAppend, %StartStopHotkey%, .\settings\settings5.txt
      FileRead, StartStopHotkey, .\settings\settings5.txt
      OutputDebug, 5= %StartStopHotkey%

      FileDelete, .\settings\settings6.txt
      FileAppend, %OpenMenu%, .\settings\settings6.txt
      FileRead, OpenMenu, .\settings\settings6.txt
      OutputDebug, 6= %OpenMenu%

      Break
}



Loop, {
      If (Paused = 0)
      {
       Random, RandomClickTIme, %RandomClickTimeMin%, %RandomClickTimeMax%
       ;Click, Left, , , , , Down
       Sleep, %LangthOfClick%
       ;Click, Left, , , , , Up
       Sleep %MillisPerClickEnd%
         MillisPerClickEnd = %MillisPerClick%
         MillisPerClickEnd += %RandomClickTIme%
         OutputDebug, %MillisPerClick%
         OutputDebug,  Click
       }
}

 StartStopHotkeyEnd:
   MillisPerClickEnd = 0
   LangthOfClick = 0
     If (Paused = 0) {
       Paused = 1
      OutputDebug,  AutoClicer is now paused
     }
     Else {
     Paused = 0
      OutputDebug,  AutoClicer is not paused
     }
Return

OpenMenuEnd:
OutputDebug, Opened Menu
Reload
Return
