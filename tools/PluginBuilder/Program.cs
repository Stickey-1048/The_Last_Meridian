using Tlm.PluginBuilder;

// Usage:
//   dotnet run --project tools/PluginBuilder -- [--out <dir>] [--fallout4-esm <path to Fallout4.esm>]
//
// Writes <dir>/TheLastMeridian.esp plus a text report and a JSON description
// read back from the written file. Default <dir> is ./build.

string outDir = "build";
string? esm = null;
float headerVersion = Builder.DefaultHeaderVersion;
for (var i = 0; i < args.Length; i++)
{
    switch (args[i])
    {
        case "--out": outDir = args[++i]; break;
        case "--fallout4-esm": esm = args[++i]; break;
        case "--header-version": headerVersion = float.Parse(args[++i], System.Globalization.CultureInfo.InvariantCulture); break;
        case "-h" or "--help":
            Console.WriteLine("PluginBuilder [--out <dir>] [--fallout4-esm <path>] [--header-version 0.95|1.0]");
            return 0;
        default:
            Console.Error.WriteLine($"unknown argument: {args[i]}");
            return 2;
    }
}

if (esm != null && !File.Exists(esm))
{
    Console.Error.WriteLine($"Fallout4.esm not found at: {esm}");
    return 2;
}

var formKeys = Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "formkeys.txt");
formKeys = Path.GetFullPath(formKeys);

var (mod, builder) = Builder.Create(formKeys, esm, headerVersion);
var plugin = Path.Combine(outDir, Spec.PluginName);
Builder.Write(mod, plugin);

// Describe what was actually written, not what we meant to write.
var info = Report.Read(plugin);
File.WriteAllText(Path.Combine(outDir, "TheLastMeridian.report.txt"), Report.ToText(info, builder.Pending, builder.VanillaNotes));
File.WriteAllText(Path.Combine(outDir, "TheLastMeridian.json"), Report.ToJson(info));

var problems = SelfCheck.Run(info);
Console.WriteLine($"{plugin}: {new FileInfo(plugin).Length} bytes, mode={(esm == null ? "skeleton (no Fallout4.esm)" : "full")}, header version {info.HeaderVersion:0.00}, lowest FormID 0x{info.LowestFormId:X}");
Console.WriteLine($"  {info.Records.Count} simple records, {info.Messages.Count} messages, {info.Quests.Count} quests, " +
                  $"{info.Quests.Sum(q => q.Stages.Count)} stages, {info.Quests.Sum(q => q.Aliases.Count)} aliases");
Console.WriteLine($"  not wired yet: {builder.Pending.Count} (see TheLastMeridian.report.txt)");
foreach (var note in builder.VanillaNotes) Console.WriteLine($"  lookup: {note}");
if (problems.Count > 0)
{
    Console.Error.WriteLine($"SELF-CHECK FAILED ({problems.Count}):");
    foreach (var p in problems) Console.Error.WriteLine("  " + p);
    return 1;
}
Console.WriteLine("  self-check: the file read back matches the spec");
return 0;
