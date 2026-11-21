using System.IO.Compression;
using System.Security.Cryptography;
using System.Text.Json;
internal static class OwnedAssets {
 internal static void Verify(string source){
  using var meta=JsonDocument.Parse(File.ReadAllText(Path.Combine(SafeBuild.ProjectRoot,"facegen-metadata.json")));
  foreach(var group in meta.RootElement.GetProperty("entries").EnumerateArray().GroupBy(e=>e.GetProperty("archive").GetString()!)){
   if(group.Key is not ("Fallout4 - Meshes.ba2" or "Fallout4 - MeshesExtra.ba2"))throw new InvalidDataException("Unexpected owned archive");
   string archive=Path.Combine(Path.GetDirectoryName(source)!,group.Key);if((File.GetAttributes(archive)&FileAttributes.ReparsePoint)!=0)throw new InvalidDataException("Redirected owned archive");
   using var file=new FileStream(archive,FileMode.Open,FileAccess.Read,FileShare.Read);using var br=new BinaryReader(file);
   if(new string(br.ReadChars(4))!="BTDX"||br.ReadUInt32()!=1||new string(br.ReadChars(4))!="GNRL")throw new InvalidDataException("Bad owned archive format");uint count=br.ReadUInt32();ulong names=br.ReadUInt64();if(count>200000||names>=(ulong)file.Length)throw new InvalidDataException("Bad owned index");
   var rows=new (ulong Offset,uint Packed,uint Unpacked)[count];for(int i=0;i<count;i++){file.Position+=16;rows[i]=(br.ReadUInt64(),br.ReadUInt32(),br.ReadUInt32());file.Position+=4;}
   var expected=group.ToDictionary(e=>e.GetProperty("path").GetString()!,e=>e.GetProperty("sha256").GetString()!,StringComparer.OrdinalIgnoreCase);var seen=new HashSet<string>(StringComparer.OrdinalIgnoreCase);file.Position=(long)names;
   for(int i=0;i<count;i++){
    string name=System.Text.Encoding.ASCII.GetString(br.ReadBytes(br.ReadUInt16())).Replace('\\','/');if(!expected.TryGetValue(name,out var hash))continue;
    if(!seen.Add(name)||rows[i].Unpacked>4000000)throw new InvalidDataException("Bad selected NIF size/duplicate");long resume=file.Position;file.Position=(long)rows[i].Offset;byte[] bytes=br.ReadBytes((int)(rows[i].Packed==0?rows[i].Unpacked:rows[i].Packed));
    if(rows[i].Packed!=0){using var memory=new MemoryStream(bytes);using var z=new ZLibStream(memory,CompressionMode.Decompress);using var output=new MemoryStream();z.CopyTo(output);bytes=output.ToArray();}
    if(bytes.Length!=rows[i].Unpacked||Convert.ToHexString(SHA256.HashData(bytes))!=hash)throw new InvalidDataException("Measured owned NIF changed: "+name);file.Position=resume;
   }if(seen.Count!=expected.Count)throw new InvalidDataException("Missing selected owned NIF");
  }
 }
}
