if ((Test-Path Function:\TabExpansion) -and -not (Test-Path Function:\completerTabExpansionBackup)) {
    Rename-Item Function:\TabExpansion completerTabExpansionBackup
}


function TabExpansion($line, $lastWord){
	$tasks = @(python "/Users/radtomas/PycharmProjects/sufler/backends/powershell/powershell.py" $line $lastWord)
	$lastOption = $line.Split(' ')[-1]

    if($tasks -match "^$lastOption"){
        $tasks | Where-Object {$_ -match "^$lastOption.*"} | Foreach {
        if($Matches[0] -eq "^$lastOption"){
            "$lastOption "
            }
        else{
            $Matches[0]
            }
        }
    }

    elseif (Test-Path Function:\completerTabExpansionBackup) {
        # Fall back on existing tab expansion
        completerTabExpansionBackup $line $lastWord
    }
}