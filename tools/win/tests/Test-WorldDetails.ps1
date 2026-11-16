<# Variant/lifecycle fixtures only. No real processes, manager or game launched. #>
param([Parameter(Mandatory)][string]$CoreArtifact,[string]$DetailsBundle,[string]$NaturalWorld,[string]$FenceWorld,[string]$CombinedWorld)
$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSScriptRoot '../Tlm.psm1') -Force
Import-Module (Join-Path $PSScriptRoot '../World-Story.psm1') -Force
$module=Get-Module World-Story
& $module {
 $script:blocked=$false;$script:unknown=$false
 function script:Get-Process {[CmdletBinding()]param() @()}
 function script:Get-CimInstance {[CmdletBinding()]param($ClassName,$Filter)
  if($script:unknown){throw 'fixture unreadable inventory'}
  if($script:blocked){[pscustomobject]@{ProcessId=501;Name='Fallout4.exe'}}
 }
}
function Inventory($busy=$false,$unknown=$false){& $module {param($b,$u)$script:blocked=$b;$script:unknown=$u} $busy $unknown}
$root=Join-Path ([IO.Path]::GetTempPath()) ('TlmDetailsTest_'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory $root)
$checks=0
function Assert($value,$label){if(!$value){throw $label};$script:checks++}
function Refuses([scriptblock]$action,$label){$failed=$false;try{& $action}catch{$failed=$true};Assert $failed $label}
try {
 $variant=Get-WorldStoryVariant -Details
 Assert ($variant.Id-ceq'details'-and$variant.ProfileName-ceq'TLM-World-Details-Preview'-and$variant.ModName-ceq'TheLastMeridian-WorldDetailsPreview'-and$variant.JournalName-ceq'world-details.unfinished.json') 'dedicated Details identities'
 foreach($other in @('Expanded','Natural')){$flags=@{Details=$true};$flags[$other]=$true;Refuses {Get-WorldStoryVariant @flags} 'ambiguous Details selection rejected'}
 Refuses {Get-WorldStoryVariant -Expanded -Natural -Details} 'all variants rejected together'
 $fixed=Get-Content $variant.ManifestPath -Raw | ConvertFrom-Json
 $natural=Get-Content (Get-WorldStoryVariant -Natural).ManifestPath -Raw | ConvertFrom-Json
 Assert ($fixed.worldSha256-ceq'E1279E42DAA19D94A628F1270D285EB8A175EE21579924C0DE51B017C25F5965'-and$fixed.masterSha256-ceq$natural.masterSha256) 'shelter only E127 and same AA52'
 Assert (($fixed.runtime|ConvertTo-Json -Compress)-ceq($natural.runtime|ConvertTo-Json -Compress)-and@($fixed.runtime.PSObject.Properties).Count-eq19) 'same normal19; no private Core'
 Assert ($fixed.detailsSource-ceq'e69c306e4cebbc2604867cb7e980418b172e0ecb') 'manifest binds accepted six-prop source'
 Assert ($natural.worldSha256-ceq'B056F66D23D18BA7D156177C64B67552B10B2A74234C78139FBDCD5AED660723') 'natural control unchanged'
 $game=Join-Path $root game;$mo=Join-Path $root manager
 $profile=Join-Path $mo ('profiles/'+$variant.ProfileName);$mod=Join-Path $mo ('mods/'+$variant.ModName)
 [void](New-Item -ItemType Directory -Force $game,$profile,(Join-Path $mod 'Scripts/TLM'))
 Set-Content (Join-Path $mo ModOrganizer.ini) "[General]`ngamePath=$game"
 Set-Content (Join-Path $game Fallout4.exe) 'fixture; never executed'
 Set-Content (Join-Path $profile settings.ini) "[General]`nLocalSaves=true`nLocalSettings=true"
 $mods=Join-Path $profile modlist.txt;Set-Content $mods ('+'+$variant.ModName)
 Set-Content (Join-Path $profile plugins.txt) "*TheLastMeridian.esp`n*TLMWorldSlice.esp"
 $world=Join-Path $mod TLMWorldSlice.esp;$core=Join-Path $mod TheLastMeridian.esp
 Copy-Item -LiteralPath $CoreArtifact -Destination $core
 Set-Content $world 'fixture details world'
 $pins=$fixed|ConvertTo-Json -Depth 6|ConvertFrom-Json
 foreach($p in $pins.runtime.PSObject.Properties){$file=Join-Path $mod ('Scripts/TLM/'+$p.Name);Set-Content $file ('fixture-'+$p.Name);$p.Value=(Get-FileHash $file).Hash}
 $pins.masterSha256=(Get-FileHash $core).Hash;$pins.worldSha256=(Get-FileHash $world).Hash
 $fixture=Join-Path $root fixture.json;$pins|ConvertTo-Json -Depth 6|Set-Content $fixture
 function Context {Get-WorldStoryContext -ModOrganizerRoot $mo -Details -ManifestPath $fixture}
 Assert ((Context).Profile-ceq$profile) 'Details isolated context accepted'
 foreach($other in @((Get-WorldStoryVariant),(Get-WorldStoryVariant -Expanded),(Get-WorldStoryVariant -Natural))){
  Refuses {Get-WorldStoryContext -ModOrganizerRoot $mo -Details -ProfileName $other.ProfileName -ManifestPath $fixture} 'Details cannot select another profile'
  Add-Content $mods ('+'+$other.ModName);Refuses {Context} 'other Meridian mod rejected';Set-Content $mods ('+'+$variant.ModName)
 }
 Add-Content $world 'wrong';Refuses {Context} 'wrong world refused';Set-Content $world 'fixture details world'
 $runtime=Join-Path $mod Scripts/TLM/Core.pex;$saved=[IO.File]::ReadAllBytes($runtime)
 Set-Content $runtime 'private Core';Refuses {Context} 'private Core cannot satisfy normal runtime';[IO.File]::WriteAllBytes($runtime,$saved)
 $ini=Join-Path $profile fallout4custom.ini;Set-Content $ini "[General]`nsStartingConsoleCommand=`nbAlwaysActive=0`nUnrelated=keep"
 $plan=Get-WorldStoryStartupPlan $game -Details
 Assert ($plan.Variant-ceq'details'-and$plan.Content-ceq(Get-WorldStoryStartupPlan $game -Natural).Content) 'same fresh queued entry; only variant identity differs'
 $note=[pscustomobject]@{Variant=$variant.Id;ProfileName=$variant.ProfileName;Ini=$ini;GameFolder=$game;StartupBefore='';ActiveBefore='0';Batch=$plan}
 $journal=Join-Path $root $variant.JournalName;$note|ConvertTo-Json -Depth 4|Set-Content $journal
 $tokens=$null;$errors=$null;$ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot '../Play-WorldStory.ps1'),[ref]$tokens,[ref]$errors)
 Assert ($errors.Count-eq0) 'actual launcher parses'
 $callbackAst=@($ast.FindAll({param($n)$n-is[Management.Automation.Language.ScriptBlockExpressionAst]-and$n.Extent.Text-match'param\(\$p\).*Set-Content'},$true))[0]
 $body=$callbackAst.Extent.Text;$callback=[scriptblock]::Create($body.Substring(1,$body.Length-2)).GetNewClosure()
 Write-FreshDemoStartupBatch $plan -OnStateChanged $callback
 $record=Get-Content $journal -Raw|ConvertFrom-Json
 Assert ($record.Batch.CreationState-ceq'Owned'-and$record.Batch.Hash-ceq$plan.Hash) 'actual inline callback persists CreateNew ownership; no lost helper-function scope'
 Set-IniValue $ini General sStartingConsoleCommand $plan.Command;Set-IniValue $ini General bAlwaysActive 1
 $try=@($ast.EndBlock.Statements|Where-Object {$_-is[Management.Automation.Language.TryStatementAst]})[-1]
 $body=$try.Finally.Extent.Text;$cleanup=[scriptblock]::Create($body.Substring(1,$body.Length-2))
 $context=[pscustomobject]@{Mo=[pscustomobject]@{GamePath=$game}}
 $otherJournal=Join-Path $root world-natural.unfinished.json;Set-Content $otherJournal 'unrelated preserved';$otherHash=(Get-FileHash $otherJournal).Hash
 foreach($mode in @('busy','unknown','wrongvariant','wrongprofile','wrongbatch')){
  $good=$note;$note=$good|ConvertTo-Json -Depth 4|ConvertFrom-Json
  switch($mode){busy {Inventory $true};unknown {Inventory $false $true};wrongvariant {$note.Variant='natural'};wrongprofile {$note.ProfileName='TLM-World-Natural-Preview'};wrongbatch {$note.Batch.Variant='natural'}}
  $a=(Get-FileHash $ini).Hash;$b=(Get-FileHash $plan.Path).Hash;$c=(Get-FileHash $journal).Hash
  Refuses {& $cleanup} 'unsafe Details cleanup refused'
  Assert ((Get-FileHash $ini).Hash-ceq$a-and(Get-FileHash $plan.Path).Hash-ceq$b-and(Get-FileHash $journal).Hash-ceq$c) 'refusal preserves settings/batch/journal'
  $note=$good;Inventory
 }
 & $cleanup
 Assert (!(Test-Path $plan.Path)-and!(Test-Path $journal)-and(Get-FileHash $otherJournal).Hash-ceq$otherHash) 'Details removes only its owned batch/note'
 Assert ((Get-IniValue $ini General sStartingConsoleCommand)-ceq''-and(Get-IniValue $ini General bAlwaysActive)-eq'0'-and(Get-IniValue $ini General Unrelated)-ceq'keep') 'Details restores startup baseline and preserves unrelated setting'
 if($DetailsBundle){
  Copy-Item (Join-Path $DetailsBundle '*.esp') $mod -Force
  Copy-Item (Join-Path $DetailsBundle 'Scripts/TLM/*.pex') (Join-Path $mod Scripts/TLM) -Force
  Assert ((Get-WorldStoryContext -ModOrganizerRoot $mo -Details).World-ceq$world) 'actual E127/AA52/normal19 package satisfies fixed Details pins'
  $saved=[IO.File]::ReadAllBytes($world);Add-Content $world 'foreignvariant';Refuses {Get-WorldStoryContext -ModOrganizerRoot $mo -Details} 'foreign world rejected by fixed Details pins';[IO.File]::WriteAllBytes($world,$saved)
  foreach($foreign in @($NaturalWorld,$FenceWorld,$CombinedWorld)|Where-Object {$_}){
   Copy-Item -LiteralPath $foreign -Destination $world -Force
   Refuses {Get-WorldStoryContext -ModOrganizerRoot $mo -Details} 'natural/fence/combined artifact cannot enter Details variant'
   [IO.File]::WriteAllBytes($world,$saved)
   Assert ((Get-WorldStoryContext -ModOrganizerRoot $mo -Details).World-ceq$world) 'Details positive context restored after foreign artifact refusal'
  }
 }
 Assert ('Details'-in@($ast.ParamBlock.Parameters|ForEach-Object {$_.Name.VariablePath.UserPath})) 'explicit owner Details switch exists'
 Write-Host "$checks Details variant/lifecycle checks passed; fixtures only, no game/manager execution."
} finally {
 $target=[IO.Path]::GetFullPath($root);$parent=[IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd([IO.Path]::DirectorySeparatorChar)+[IO.Path]::DirectorySeparatorChar
 if(!$target.StartsWith($parent,[StringComparison]::OrdinalIgnoreCase)-or[IO.Path]::GetFileName($target)-notlike'TlmDetailsTest_*'){throw 'Fixture cleanup escaped its named temporary directory.'}
 Remove-Item -LiteralPath $target -Recurse -Force;Remove-Module World-Story
}
