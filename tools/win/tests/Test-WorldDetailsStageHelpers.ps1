param([string]$Stager=(Join-Path $PSScriptRoot '../Stage-WorldDetails.ps1'),[string]$Module=(Join-Path $PSScriptRoot '../Tlm.psm1'))
$ErrorActionPreference='Stop'
Import-Module $Module -Force
$tokens=$null;$errors=$null;$ast=[Management.Automation.Language.Parser]::ParseFile((Resolve-Path $Stager),[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'Stager parse failed'}
# Define only selected pure helpers, never execute the stager body.
foreach($name in @('Assert-DetailsStagePath','Copy-DetailsStageNewFile','Get-DetailsOtherPrefs')){
 $function=@($ast.FindAll({param($n)$n-is[Management.Automation.Language.FunctionDefinitionAst]-and$n.Name-ceq$name},$false))[0]
 . ([scriptblock]::Create($function.Extent.Text))
}
function Assert-DetailsStageClear {} # No real process query in fixtures.
$root=Join-Path ([IO.Path]::GetTempPath()) ('TlmDetailsStage_'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory $root)
$mock=@{Reparse='';Unreadable=''};$checks=0
function Get-Item {
 [CmdletBinding()]param([string]$LiteralPath,[switch]$Force)
 if($LiteralPath-ceq$mock.Unreadable){throw 'fixture unreadable ancestry'}
 $entry=Microsoft.PowerShell.Management\Get-Item -LiteralPath $LiteralPath -Force:$Force -ErrorAction Stop
 if($LiteralPath-ceq$mock.Reparse){return [pscustomobject]@{Attributes=([IO.FileAttributes]::Directory-bor[IO.FileAttributes]::ReparsePoint);PSIsContainer=$true}}
 $entry
}
function Assert($value,$label){if(!$value){throw $label};$script:checks++}
function Refuses([scriptblock]$action,$label){$failed=$false;try{& $action}catch{$failed=$true};Assert $failed $label}
try{
 $source=Join-Path $root source.txt;$dest=Join-Path $root new.txt;Set-Content $source 'unchanged source';$hash=(Get-FileHash $source).Hash
 Copy-DetailsStageNewFile $source $dest
 Assert ((Get-FileHash $dest).Hash-ceq$hash) 'CreateNew exact copy'
 Refuses {Copy-DetailsStageNewFile $source $dest} 'existing identical destination refused'
 Assert ((Get-FileHash $dest).Hash-ceq$hash) 'existing target preserved'
 $empty=Join-Path $root empty;[void](New-Item -ItemType Directory $empty)
 Refuses {Assert-DetailsStagePath $empty -New} 'existing empty target refused'
 $new=Join-Path $root blocked.txt
 $mock.Reparse=$root;Refuses {Copy-DetailsStageNewFile $source $new} 'reparse ancestor blocks copy';Assert (!(Test-Path $new)) 'reparse refusal created nothing';$mock.Reparse=''
 $mock.Unreadable=$root;Refuses {Copy-DetailsStageNewFile $source $new} 'unreadable ancestor blocks copy';Assert (!(Test-Path $new)) 'unreadable refusal created nothing';$mock.Unreadable=''
 $prefs=Join-Path $root prefs.ini;Set-Content $prefs "[General]`r`nbGamepadEnable=0`r`nKeep=unchanged`r`n[Display]`r`niSize W=1920"
 $before=@(Get-DetailsOtherPrefs $prefs)
 Set-IniValue $prefs General bGamepadEnable 1
 Assert ((Get-IniValue $prefs General bGamepadEnable)-eq'1') 'new profile controller enabled'
 Assert ([string]::Join("`n",@(Get-DetailsOtherPrefs $prefs))-ceq[string]::Join("`n",$before)) 'all other preference lines preserved'
 Assert ((Get-FileHash $source).Hash-ceq$hash) 'source never changed'
 Write-Host "$checks Details stager helper checks passed; only temp fixtures, no installed writes or process inspection."
}finally{
 $target=[IO.Path]::GetFullPath($root);$parent=[IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd([IO.Path]::DirectorySeparatorChar)+[IO.Path]::DirectorySeparatorChar
 if(!$target.StartsWith($parent,[StringComparison]::OrdinalIgnoreCase)-or[IO.Path]::GetFileName($target)-notlike'TlmDetailsStage_*'){throw 'Fixture cleanup escaped named temp root'}
 Remove-Item -LiteralPath $target -Recurse -Force
}
