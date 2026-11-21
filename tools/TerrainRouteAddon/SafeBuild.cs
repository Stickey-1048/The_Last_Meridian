using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Win32.SafeHandles;

// Windows-only local prototype guard. No cleanup/adoption/retry behavior.
internal sealed class SafeBuild : IDisposable
{
    internal const string OwnedMasterSha256="AE7BE31A59052F926474A767D9DBFBCC7F19AF4AD2070491F7F40D821B2520EB";
    static string ProjectFile([CallerFilePath] string path="")=>path;
    internal static string ProjectRoot=>Path.GetDirectoryName(ProjectFile())!;
    internal string Source {get;}
    internal string Output {get;}
    internal string SourceHash {get;}
    readonly Dictionary<string,SafeFileHandle> directories=new(StringComparer.OrdinalIgnoreCase);
    readonly FileStream sourceLock;
    readonly string buildRoot;
    bool created;
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
    static extern SafeFileHandle CreateFileW(string path,uint access,uint share,IntPtr security,uint disposition,uint flags,IntPtr template);
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
    static extern bool CreateDirectoryW(string path,IntPtr security);
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
    static extern uint GetFinalPathNameByHandleW(SafeFileHandle file,StringBuilder path,uint length,uint flags);
    [DllImport("kernel32.dll",SetLastError=true)]
    static extern bool GetFileInformationByHandleEx(SafeFileHandle file,int kind,out AttributeTag info,uint size);
    [StructLayout(LayoutKind.Sequential)] struct AttributeTag {public uint Attributes;public uint Tag;}
    static InvalidDataException Refuse(string why)=>new("REFUSED: "+why);
    static bool Within(string path,string directory)=>path.StartsWith(directory.TrimEnd('\\')+"\\",StringComparison.OrdinalIgnoreCase);
    static void Lexical(string raw,bool absolute){
        if(string.IsNullOrWhiteSpace(raw)||raw!=raw.Trim()||raw.Contains('\0'))throw Refuse("empty or padded path");
        string p=raw.Replace('/','\\');
        if(p.StartsWith("\\")||p.Contains("\\\\")||p.IndexOf(':',absolute?2:0)>=0)throw Refuse("UNC/device/alternate-stream/drive-relative path");
        if(absolute&&(!Path.IsPathFullyQualified(p)||p.Length<3||!char.IsAsciiLetter(p[0])||p[1]!=':'||p[2]!='\\'))throw Refuse("input must be an absolute local drive path");
        foreach(string segment in (absolute?p[3..]:p).Split('\\')){
            string head=segment.Split('.')[0].ToUpperInvariant();
            if(segment.Length==0||segment is "." or ".."||segment.EndsWith(' ')||segment.EndsWith('.')||segment.IndexOfAny(new[]{'<','>','"','|','?','*',':'})>=0||head is "CON" or "PRN" or "AUX" or "NUL"||head.Length==4&&(head.StartsWith("COM")||head.StartsWith("LPT"))&&head[3]>='1'&&head[3]<='9')throw Refuse("unsafe path component/traversal");
        }
    }
    static FileAttributes? Attributes(string path){
        try{return File.GetAttributes(path);}
        catch(FileNotFoundException){return null;}
        catch(DirectoryNotFoundException){return null;}
    }
    void LockDirectory(string path){
        if(directories.ContainsKey(path))return;
        var attr=Attributes(path)??throw Refuse("missing directory ancestor");
        if((attr&FileAttributes.ReparsePoint)!=0)throw Refuse("reparse/junction ancestor");
        if((attr&FileAttributes.Directory)==0)throw Refuse("non-directory ancestor");
        // Hold read-attribute handles without WRITE/DELETE sharing, preventing
        // ancestor replacement/reparse mutation while output is being written.
        var handle=CreateFileW(path,0x00100081,1,IntPtr.Zero,3,0x02200000,IntPtr.Zero);
        if(handle.IsInvalid){handle.Dispose();throw Refuse("cannot lock directory ancestor: "+new Win32Exception(Marshal.GetLastWin32Error()).Message);}
        try{
            if(!GetFileInformationByHandleEx(handle,9,out var info,8)||(info.Attributes&0x400)!=0||(info.Attributes&0x10)==0)throw Refuse("directory changed to reparse/non-directory");
            var final=new StringBuilder(32768);uint n=GetFinalPathNameByHandleW(handle,final,(uint)final.Capacity,0);
            if(n==0||n>=final.Capacity)throw Refuse("cannot resolve locked ancestor");
            string resolved=final.ToString();if(resolved.StartsWith("\\\\?\\"))resolved=resolved[4..];
            if(!resolved.TrimEnd('\\').Equals(path.TrimEnd('\\'),StringComparison.OrdinalIgnoreCase))throw Refuse("ancestor final path differs");
            directories.Add(path,handle);
        }catch{handle.Dispose();throw;}
    }
    void LockAncestors(string path,bool finalMayBeMissing){
        var missing=false;string cursor=Path.GetPathRoot(path)!;LockDirectory(cursor);
        foreach(string segment in path[cursor.Length..].Split('\\',StringSplitOptions.RemoveEmptyEntries)){
            cursor=Path.Combine(cursor,segment);var attr=Attributes(cursor);
            if(attr==null){missing=true;if(!finalMayBeMissing)throw Refuse("missing input ancestor");continue;}
            if(missing)throw Refuse("unexpected existing path under missing ancestor");
            LockDirectory(cursor);
        }
    }
    SafeBuild(string input,string destination){
        if(!OperatingSystem.IsWindows())throw Refuse("Windows local-path guard required");
        Lexical(input,true);
        bool absolute=Path.IsPathFullyQualified(destination);Lexical(destination,absolute);
        Source=Path.GetFullPath(input);Output=Path.GetFullPath(destination,ProjectRoot);buildRoot=Path.Combine(ProjectRoot,"build");
        if(!Path.GetFileName(Source).Equals("Fallout4.esm",StringComparison.OrdinalIgnoreCase))throw Refuse("owned-master filename mismatch");
        if(!Within(Output,buildRoot)||!Path.GetDirectoryName(Output)!.Equals(buildRoot,StringComparison.Ordinal))throw Refuse("output must be one fresh directory directly under actual project build root");
        if(Source.Equals(Output,StringComparison.OrdinalIgnoreCase)||Within(Source,Output))throw Refuse("source must stay outside output");
        try{
            LockAncestors(ProjectRoot,false);
            if(!File.Exists(Path.Combine(ProjectRoot,"TerrainPrototype.csproj")))throw Refuse("bound project file missing");
            LockAncestors(Path.GetDirectoryName(Source)!,false);
            LockAncestors(Path.GetDirectoryName(Output)!,true);
            if(Attributes(Output)!=null)throw Refuse("existing destination (never adopted)");
            var sourceAttr=Attributes(Source)??throw Refuse("owned input missing");
            if((sourceAttr&(FileAttributes.ReparsePoint|FileAttributes.Directory))!=0)throw Refuse("input is reparse/directory");
            sourceLock=new FileStream(Source,FileMode.Open,FileAccess.Read,FileShare.Read);
            if(!GetFileInformationByHandleEx(sourceLock.SafeFileHandle,9,out var fileInfo,8)||(fileInfo.Attributes&0x410)!=0)throw Refuse("opened input became reparse/directory");
            var sourceFinal=new StringBuilder(32768);uint finalLength=GetFinalPathNameByHandleW(sourceLock.SafeFileHandle,sourceFinal,(uint)sourceFinal.Capacity,0);
            string actual=sourceFinal.ToString();if(actual.StartsWith("\\\\?\\"))actual=actual[4..];
            if(finalLength==0||finalLength>=sourceFinal.Capacity||!actual.Equals(Source,StringComparison.OrdinalIgnoreCase))throw Refuse("opened input final path differs");
            SourceHash=Convert.ToHexString(SHA256.HashData(sourceLock));sourceLock.Position=0;
            if(SourceHash!=OwnedMasterSha256)throw Refuse("owned-master SHA256 mismatch");
        }catch{foreach(var handle in directories.Values)handle.Dispose();sourceLock?.Dispose();throw;}
    }
    internal static SafeBuild Open(string input,string destination)=>new(input,destination);
    void ExclusiveDirectory(string path){
        if(!CreateDirectoryW(path,IntPtr.Zero))throw Refuse("directory create refused (no adoption): "+new Win32Exception(Marshal.GetLastWin32Error()).Message);
        LockDirectory(path);
    }
    internal void CreateOutput(){
        if(created)throw Refuse("output already claimed");
        if(Attributes(buildRoot)==null)ExclusiveDirectory(buildRoot);else LockDirectory(buildRoot);
        // All source/hash/path checks happened before this first output write.
        if(Attributes(Output)!=null)throw Refuse("destination appeared after preflight");
        ExclusiveDirectory(Output);created=true;
    }
    internal void WriteNew(string name,byte[] data){
        if(!created||Path.GetFileName(name)!=name||name.IndexOfAny(new[]{'/','\\',':'})>=0)throw Refuse("unclaimed output or unsafe filename");
        LockDirectory(Output);
        using var stream=new FileStream(Path.Combine(Output,name),FileMode.CreateNew,FileAccess.Write,FileShare.None);
        stream.Write(data);stream.Flush(true);
    }
    public void Dispose(){sourceLock.Dispose();foreach(var h in directories.Values.Reverse())h.Dispose();}
}
