using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Win32.SafeHandles;
internal sealed class LockedInput:IDisposable {
 internal string Path{get;}internal string Hash{get;}readonly FileStream file;
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]static extern uint GetFinalPathNameByHandleW(SafeFileHandle h,StringBuilder s,uint n,uint flags);
 LockedInput(string path,string hash){
  Path=System.IO.Path.GetFullPath(path);string? cursor=Path;
  while(cursor!=null){var a=File.GetAttributes(cursor);if((a&FileAttributes.ReparsePoint)!=0)throw new InvalidDataException("Redirected fixed addon input");cursor=System.IO.Path.GetDirectoryName(cursor);}
  file=new FileStream(Path,FileMode.Open,FileAccess.Read,FileShare.Read);
  try{var actual=new StringBuilder(32768);uint n=GetFinalPathNameByHandleW(file.SafeFileHandle,actual,(uint)actual.Capacity,0);string name=actual.ToString();if(name.StartsWith(@"\\?\"))name=name[4..];if(n==0||n>=actual.Capacity||!name.Equals(Path,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Input opened at unexpected path");Hash=Convert.ToHexString(SHA256.HashData(file));file.Position=0;if(Hash!=hash)throw new InvalidDataException("Frozen addon dependency hash mismatch");}catch{file.Dispose();throw;}
 }
 internal static LockedInput Open(string path,string hash)=>new(path,hash);
 public void Dispose()=>file.Dispose();
}
