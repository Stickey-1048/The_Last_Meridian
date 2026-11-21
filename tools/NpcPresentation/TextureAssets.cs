using System.IO.Compression;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.RegularExpressions;
internal static class TextureAssets {
 internal static void Verify(string source,uint[] donors){
  using var meta=JsonDocument.Parse(File.ReadAllText(Path.Combine(SafeBuild.ProjectRoot,"texture-metadata.json")));var root=meta.RootElement;
  if(root.GetProperty("missing").GetArrayLength()!=0)throw new InvalidDataException("Unresolved texture dependency");
  var entries=root.GetProperty("entries").EnumerateArray().ToDictionary(e=>e.GetProperty("path").GetString()!,e=>e,StringComparer.OrdinalIgnoreCase);
  var needed=root.GetProperty("references").EnumerateObject().SelectMany(p=>p.Value.EnumerateArray().Select(x=>x.GetString()!)).ToHashSet(StringComparer.OrdinalIgnoreCase);
  if(entries.Count!=86||!needed.SetEquals(entries.Keys))throw new InvalidDataException("Incomplete selected NIF texture inventory");
  foreach(var id in donors)foreach(var suffix in new[]{"_d.dds","_msn.dds","_s.dds"})if(!entries.ContainsKey("textures/actors/character/facecustomization/fallout4.esm/"+id.ToString("x8")+suffix))throw new InvalidDataException("Missing baked face diffuse/normal/specular");
  foreach(var group in entries.Values.GroupBy(e=>e.GetProperty("archive").GetString()!)){
   if(!Regex.IsMatch(group.Key,@"^Fallout4 - Textures[1-9]\.ba2$"))throw new InvalidDataException("Unexpected texture archive");string path=Path.Combine(Path.GetDirectoryName(source)!,group.Key);
   if((File.GetAttributes(path)&FileAttributes.ReparsePoint)!=0)throw new InvalidDataException("Redirected texture archive");
   using var file=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.Read);using var br=new BinaryReader(file);
   if(new string(br.ReadChars(4))!="BTDX"||br.ReadUInt32()!=1||new string(br.ReadChars(4))!="DX10")throw new InvalidDataException("Bad texture archive");uint n=br.ReadUInt32();ulong names=br.ReadUInt64();if(n>200000||names>=(ulong)file.Length)throw new InvalidDataException("Bad texture index");
   var expected=group.ToDictionary(e=>e.GetProperty("path").GetString()!,e=>e,StringComparer.OrdinalIgnoreCase);var selected=new Dictionary<int,JsonElement>();file.Position=(long)names;
   for(int i=0;i<n;i++){string name=System.Text.Encoding.ASCII.GetString(br.ReadBytes(br.ReadUInt16())).Replace('\\','/');if(expected.TryGetValue(name,out var e))selected.Add(i,e);}if(selected.Count!=expected.Count)throw new InvalidDataException("Selected texture missing");
   file.Position=24;for(int i=0;i<=selected.Keys.Max();i++){
    file.Position+=12;br.ReadByte();byte count=br.ReadByte();ushort chunkHeader=br.ReadUInt16(),height=br.ReadUInt16(),width=br.ReadUInt16();byte mips=br.ReadByte(),format=br.ReadByte();br.ReadUInt16();
    var chunks=new (ulong Offset,uint Packed,uint Unpacked)[count];for(int j=0;j<count;j++){chunks[j]=(br.ReadUInt64(),br.ReadUInt32(),br.ReadUInt32());file.Position+=8;}
    if(!selected.TryGetValue(i,out var e))continue;
    if(chunkHeader!=24||height!=e.GetProperty("height").GetInt32()||width!=e.GetProperty("width").GetInt32()||mips!=e.GetProperty("mips").GetInt32()||format!=e.GetProperty("dxgiFormat").GetInt32()||count!=e.GetProperty("chunks").GetInt32())throw new InvalidDataException("Texture metadata differs");
    long resume=file.Position;using var hash=IncrementalHash.CreateHash(HashAlgorithmName.SHA256);long total=0;
    foreach(var c in chunks){if(c.Unpacked>32000000||c.Packed>32000000)throw new InvalidDataException("Oversized selected texture chunk");file.Position=(long)c.Offset;byte[] bytes=br.ReadBytes((int)(c.Packed==0?c.Unpacked:c.Packed));if(c.Packed!=0){using var input=new MemoryStream(bytes);using var z=new ZLibStream(input,CompressionMode.Decompress);using var output=new MemoryStream();z.CopyTo(output);bytes=output.ToArray();}if(bytes.Length!=c.Unpacked)throw new InvalidDataException("Bad texture chunk");hash.AppendData(bytes);total+=bytes.Length;}
    if(total!=e.GetProperty("unpackedBytes").GetInt64()||Convert.ToHexString(hash.GetHashAndReset())!=e.GetProperty("unpackedSha256").GetString())throw new InvalidDataException("Actual selected DDS texture changed");file.Position=resume;
   }
  }
 }
}
