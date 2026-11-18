using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Noggog;
using Tlm.PluginBuilder;

// Invented stand-in records, numerical metadata only; no game assets/native proof.
public static class RhEnvironmentFixture
{
    public static void Add(Fallout4Mod mod,string variant){
        foreach(var expected in RedHollowEnvironment.Assets){
            if(mod.Statics.Any(s=>s.EditorID==expected.Id))continue;
            var s=mod.Statics.AddNew(expected.Id);s.Model=new Model{File=expected.Model};
            var b=expected.Bounds;s.ObjectBounds.First=new P3Int16(b[0],b[1],b[2]);s.ObjectBounds.Second=new P3Int16(b[3],b[4],b[5]);
        }
        var light=mod.Lights.AddNew("defaultLightWarm01NS");light.Radius=256;light.Time=-1;light.Flags=(Light.Flag)8193;light.FadeValue=1;light.FalloffExponent=1;light.Color=System.Drawing.Color.FromArgb(0,228,203,182);
        mod.LightingTemplates.AddNew("QuarryLightingTemplate");
        var climate=mod.Climates.AddNew("RHSyntheticClimate");var world=mod.Worldspaces.AddNew("Commonwealth");world.Climate.SetTo(climate.FormKey);
        mod.LandscapeTextures.AddNew("LDirtGravel01");
    }
}
