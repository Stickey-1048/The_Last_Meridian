using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using Tlm.PluginBuilder;

// Invented stand-in records, numerical metadata only; no game assets/native proof.
public static class RhEnvironmentFixture
{
    public static readonly string[] Variants={"rhe-no-light","rhe-light-radius","rhe-light-off","rhe-light-script","rhe-light-color","rhe-template","rhe-room-template","rhe-static-model","rhe-floor-height","rhe-no-climate","rhe-decorative-only"};
    public static void Add(Fallout4Mod mod,string variant){
        foreach(var expected in RedHollowEnvironment.Assets){
            var s=mod.Statics.SingleOrDefault(s=>s.EditorID==expected.Id)??mod.Statics.AddNew(expected.Id);s.Model=new Model{File=expected.Model};
            var b=expected.Bounds;s.ObjectBounds.First=new P3Int16(b[0],b[1],b[2]);s.ObjectBounds.Second=new P3Int16(b[3],b[4],b[5]);
        }
        var light=mod.Lights.AddNew("defaultLightWarm01NS");light.Radius=256;light.Time=-1;light.Flags=(Light.Flag)8193;light.FadeValue=1;light.FalloffExponent=1;light.Color=System.Drawing.Color.FromArgb(0,228,203,182);
        var template=mod.LightingTemplates.AddNew("QuarryLightingTemplate");template.AmbientColor=System.Drawing.Color.FromArgb(255,39,38,35);template.DirectionalColor=System.Drawing.Color.FromArgb(255,20,20,20);template.FogNear=1200;template.FogFar=10000;
        var room=new Cell(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="DunwichBorers01",Flags=Cell.Flag.IsInteriorCell};room.LightingTemplate.SetTo(template.FormKey);room.Lighting=new CellLighting{AmbientColor=System.Drawing.Color.FromArgb(255,39,38,35),FogFar=10000,Inherits=(CellLighting.Inherit)1784};
        int blockId=(int)(room.FormKey.ID%10),subId=(int)(room.FormKey.ID/10%10);var block=mod.Cells.Records.SingleOrDefault(b=>b.BlockNumber==blockId);
        if(block==null){block=new CellBlock{BlockNumber=blockId,GroupType=GroupTypeEnum.InteriorCellBlock};mod.Cells.Records.Add(block);}
        var sub=block.SubBlocks.SingleOrDefault(s=>s.BlockNumber==subId);if(sub==null){sub=new CellSubBlock{BlockNumber=subId,GroupType=GroupTypeEnum.InteriorCellSubBlock};block.SubBlocks.Add(sub);}sub.Cells.Add(room);
        var climate=mod.Climates.AddNew("RHSyntheticClimate");var world=mod.Worldspaces.AddNew("Commonwealth");world.Climate.SetTo(climate.FormKey);
        mod.LandscapeTextures.AddNew("LDirtGravel01");
        switch(variant){
            case "rhe-no-light":mod.Lights.Remove(light.FormKey);break;
            case "rhe-light-radius":light.Radius=128;break;
            case "rhe-light-off":light.Flags|=Light.Flag.OffByDefault;break;
            case "rhe-light-script":light.VirtualMachineAdapter=new VirtualMachineAdapter();light.VirtualMachineAdapter.Scripts.Add(new ScriptEntry{Name="SyntheticForbiddenBehavior"});break;
            case "rhe-light-color":light.Color=System.Drawing.Color.Black;break;
            case "rhe-template":template.AmbientColor=System.Drawing.Color.Black;break;
            case "rhe-room-template":room.LightingTemplate.SetTo(Mutagen.Bethesda.Plugins.FormKey.Null);break;
            case "rhe-static-model":mod.Statics.Single(s=>s.EditorID=="QryCubeWall01").Model!.File="Synthetic\\Unreviewed.nif";break;
            case "rhe-floor-height":mod.Statics.Single(s=>s.EditorID=="QryFloor01").ObjectBounds.Second=new P3Int16(256,256,64);break;
            case "rhe-no-climate":world.Climate.SetTo(Mutagen.Bethesda.Plugins.FormKey.Null);break;
            case "rhe-decorative-only":mod.Lights.Remove(light.FormKey);mod.Statics.AddNew("defaultLightWarm01NS").Model=new Model{File="Synthetic\\DecorativeLamp.nif"};break;
        }
    }
}
