// InkFlow_Probe — jetable, hors livraison. Journalise ce que le jeu fait des coques Ink Flow.
// Pose : r6\scripts\InkFlow_Probe\InkFlow_Probe.reds (Redscript 0.5.32 + Codeware 1.21.2 requis).
// Lecture : ModLog(n"InkFlowProbe", …) ; le fichier est retrouvé par pose_probe.py logs.
// Marqueur manuel : F9 en jeu écrit une ligne ===== MARK n (à presser avant chaque geste).
module InkFlow.Probe

public class InkFlowProbe extends ScriptableService {
  private let marks: Int32;

  private cb func OnLoad() {
    let cs = GameInstance.GetCallbackSystem();
    // Ressources : chaque chargement d'un type qui porte une coque ou son matériau.
    cs.RegisterCallback(n"Resource/Load", this, n"OnResourceLoad").AddTarget(ResourceTarget.Type(n"CMesh"));
    cs.RegisterCallback(n"Resource/Load", this, n"OnResourceLoad").AddTarget(ResourceTarget.Type(n"MorphTargetMesh"));
    cs.RegisterCallback(n"Resource/Load", this, n"OnResourceLoad").AddTarget(ResourceTarget.Type(n"appearanceAppearanceResource"));
    cs.RegisterCallback(n"Resource/Load", this, n"OnResourceLoad").AddTarget(ResourceTarget.Type(n"entEntityTemplate"));
    cs.RegisterCallback(n"Resource/Load", this, n"OnResourceLoad").AddTarget(ResourceTarget.Type(n"gameuiCharacterCustomizationInfoResource"));
    cs.RegisterCallback(n"Resource/PostLoad", this, n"OnResourcePostLoad").AddTarget(ResourceTarget.Type(n"CMesh"));
    cs.RegisterCallback(n"Resource/PostLoad", this, n"OnResourcePostLoad").AddTarget(ResourceTarget.Type(n"MorphTargetMesh"));
    // v2 : le female_cco fusionné (ArchiveXL) tel que le jeu le voit : nos switchers, leur lien, les groupes.
    cs.RegisterCallback(n"Resource/PostLoad", this, n"OnCustomizationPostLoad").AddTarget(ResourceTarget.Type(n"gameuiCharacterCustomizationInfoResource"));
    // Cycle de vie des pantins (joueur, pantin du créateur) : sans cible, filtré dans le gestionnaire.
    cs.RegisterCallback(n"Entity/Assemble", this, n"OnAssemble");
    cs.RegisterCallback(n"Entity/Reassemble", this, n"OnReassemble");
    cs.RegisterCallback(n"Entity/Attach", this, n"OnAttach");
    cs.RegisterCallback(n"Entity/AfterAttach", this, n"OnAfterAttach");
    cs.RegisterCallback(n"Entity/Detach", this, n"OnDetach");
    // Marqueurs : session et touche F9.
    cs.RegisterCallback(n"Session/Ready", this, n"OnSessionReady");
    cs.RegisterCallback(n"Session/BeforeEnd", this, n"OnSessionEnd");
    cs.RegisterCallback(n"Input/Key", this, n"OnKey").AddTarget(InputTarget.Key(EInputKey.IK_F9));
    this.marks = 0;
    ModLog(n"InkFlowProbe", "===== InkFlow_Probe loaded (Resource/Load, Resource/PostLoad, Entity/*, Session/*, F9)");
  }

  // ---------- ressources ----------

  private func Interesting(path: String) -> Bool {
    // Nos chemins, les bras / corps / tête du joueur, les tatouages vanilla, les gabarits FPP ;
    // et toute ressource dont le chemin n'est pas résolu (nos chemins peuvent être inconnus du registre).
    if StrLen(path) == 0 { return true; }
    let p = StrLower(path);
    return StrContains(p, "inkflow") || StrContains(p, "tattoo") || StrContains(p, "fpp")
      || StrContains(p, "pwa_") || StrContains(p, "t0_000_") || StrContains(p, "a0_000_")
      || StrContains(p, "h0_000_") || StrContains(p, "angel") || StrContains(p, "_cco")
      || StrContains(p, "player_wa") || StrContains(p, "customization");
  }

  private cb func OnResourceLoad(event: ref<ResourceEvent>) {
    let path = ResRef.ToString(event.GetPath());
    if !this.Interesting(path) { return; }
    let res = event.GetResource();
    let cls = IsDefined(res) ? NameToString(res.GetClassName()) : "<null resource>";
    ModLog(n"InkFlowProbe", s"LOAD      \(cls)  \(this.Show(path, event.GetPath()))");
  }

  private cb func OnResourcePostLoad(event: ref<ResourceEvent>) {
    let path = ResRef.ToString(event.GetPath());
    if !this.Interesting(path) { return; }
    let res = event.GetResource();
    let cls = IsDefined(res) ? NameToString(res.GetClassName()) : "<null resource>";
    ModLog(n"InkFlowProbe", s"POSTLOAD  \(cls)  \(this.Show(path, event.GetPath()))");
  }

  // v2 : dump du jeu de personnalisation fusionné (vanilla + ArchiveXL).
  private cb func OnCustomizationPostLoad(event: ref<ResourceEvent>) {
    let cco = event.GetResource() as gameuiCharacterCustomizationInfoResource;
    if !IsDefined(cco) { return; }
    let path = ResRef.ToString(event.GetPath());
    ModLog(n"InkFlowProbe", s"=== CCO POSTLOAD \(path)  body=\(ArraySize(cco.bodyCustomizationOptions)) arms=\(ArraySize(cco.armsCustomizationOptions)) head=\(ArraySize(cco.headCustomizationOptions)) bodyGroups=\(ArraySize(cco.bodyGroups)) perspectives=\(ArraySize(cco.perspectiveInfo))");
    let i = 0;
    while i < ArraySize(cco.bodyGroups) {
      let g = cco.bodyGroups[i];
      let ours = 0;
      let j = 0;
      let sample = "";
      while j < ArraySize(g.options) {
        let on = StrLower(NameToString(g.options[j]));
        if StrContains(on, "inkflow") {
          ours += 1;
          if ours <= 3 { sample += " " + on; }
        }
        j += 1;
      }
      ModLog(n"InkFlowProbe", s"  group \(NameToString(g.name))  options=\(ArraySize(g.options))  inkflow=\(ours) \(sample)");
      i += 1;
    }
    i = 0;
    while i < ArraySize(cco.perspectiveInfo) {
      let p = cco.perspectiveInfo[i];
      ModLog(n"InkFlowProbe", s"  perspective \(NameToString(p.name))  fpp=\(NameToString(p.fpp))  tpp=\(NameToString(p.tpp))");
      i += 1;
    }
    i = 0;
    while i < ArraySize(cco.bodyCustomizationOptions) {
      let sw = cco.bodyCustomizationOptions[i] as gameuiSwitcherInfo;
      if IsDefined(sw) {
        let nm = StrLower(NameToString(sw.name));
        if StrContains(nm, "inkflow") || StrContains(nm, "tattoo") || StrContains(nm, "nipples") {
          let slots = "";
          let j = 0;
          while j < ArraySize(sw.uiSlots) { slots += " " + NameToString(sw.uiSlots[j]); j += 1; }
          ModLog(n"InkFlowProbe", s"  switcher \(NameToString(sw.name))  index=\(sw.index)  link=\(NameToString(sw.link))  linkController=\(sw.linkController)  hidden=\(sw.hidden)  enabled=\(sw.enabled)  options=\(ArraySize(sw.options))  tags=\(ArraySize(sw.editTags))  uiSlots=[\(slots) ]");
        }
      }
      i += 1;
    }
  }

  private func Show(path: String, ref: ResRef) -> String {
    if StrLen(path) == 0 { return s"<unresolved path> hash=\(ResRef.GetHash(ref))"; }
    return s"\(path)";
  }

  // ---------- entités ----------

  private func IsPuppet(entity: wref<Entity>) -> Bool {
    if !IsDefined(entity) { return false; }
    if !entity.IsA(n"gamePuppet") { return false; }
    let tpl = StrLower(ResRef.ToString(entity.GetTemplatePath()));
    return StrContains(tpl, "player") || StrContains(tpl, "customization") || entity.IsA(n"PlayerPuppet");
  }

  private cb func OnAssemble(event: ref<EntityLifecycleEvent>) {
    this.Dump("ASSEMBLE", event.GetEntity());
  }
  private cb func OnReassemble(event: ref<EntityLifecycleEvent>) {
    this.Dump("REASSEMBLE", event.GetEntity());
  }
  private cb func OnAttach(event: ref<EntityLifecycleEvent>) {
    this.Dump("ATTACH", event.GetEntity());
  }
  private cb func OnAfterAttach(event: ref<EntityLifecycleEvent>) {
    this.Dump("AFTERATTACH", event.GetEntity());
  }
  private cb func OnDetach(event: ref<EntityLifecycleEvent>) {
    let entity = event.GetEntity();
    if !this.IsPuppet(entity) { return; }
    ModLog(n"InkFlowProbe", s"DETACH    \(NameToString(entity.GetClassName()))  \(ResRef.ToString(entity.GetTemplatePath()))");
  }

  private func Dump(stage: String, entity: wref<Entity>) {
    if !this.IsPuppet(entity) { return; }
    let comps = entity.GetComponents();
    let total = ArraySize(comps);
    let shown = 0;
    ModLog(n"InkFlowProbe", s"--- \(stage)  \(NameToString(entity.GetClassName()))  \(ResRef.ToString(entity.GetTemplatePath()))  components=\(total)");
    let i = 0;
    while i < total {
      if this.DumpComponent(comps[i]) { shown += 1; }
      i += 1;
    }
    ModLog(n"InkFlowProbe", s"--- end \(stage)  shown=\(shown)/\(total)");
  }

  // Retourne vrai si la ligne a été écrite.
  private func DumpComponent(comp: ref<IComponent>) -> Bool {
    let name = NameToString(comp.GetName());
    let cls = NameToString(comp.GetClassName());
    let skinned = comp as entSkinnedMeshComponent;
    let morph = comp as entMorphTargetSkinnedMeshComponent;
    let path: ResRef;
    let hash: Uint64;
    let extra: String = "";
    if IsDefined(skinned) {
      path = ResourceAsyncRef.GetPath(skinned.mesh);
      hash = ResourceAsyncRef.GetHash(skinned.mesh);
      extra = s"app=\(NameToString(skinned.meshAppearance)) chunkMask=\(skinned.chunkMask) renderPlane=\(NameToString(skinned.renderingPlaneAnimationParam)) visParam=\(NameToString(skinned.visibilityAnimationParam)) order=\(skinned.order) isEnabledField=\(skinned.isEnabled)";
    } else if IsDefined(morph) {
      path = ResourceAsyncRef.GetPath(morph.morphResource);
      hash = ResourceAsyncRef.GetHash(morph.morphResource);
      extra = s"app=\(NameToString(morph.meshAppearance)) chunkMask=\(morph.chunkMask)";
    } else {
      return false;
    }
    let pathStr = ResRef.ToString(path);
    let interesting = this.Interesting(pathStr) || this.Interesting(name);
    if !interesting { return false; }
    // État de chargement de la ressource du composant, vu du dépôt (déjà en cache ou non, échouée ou non).
    let state = "n/a";
    if hash != 0ul {
      let depot = GameInstance.GetResourceDepot();
      let exists = depot.ResourceExists(path);
      let token = depot.LoadResource(path);
      if IsDefined(token) {
        state = s"exists=\(exists) finished=\(token.IsFinished()) loaded=\(token.IsLoaded()) failed=\(token.IsFailed())";
      } else {
        state = s"exists=\(exists) token=null";
      }
    }
    let shownPath = StrLen(pathStr) == 0 ? s"<unresolved> hash=\(hash)" : pathStr;
    ModLog(n"InkFlowProbe", s"  \(cls)  name=\(name)  enabled=\(comp.IsEnabled())  mesh=\(shownPath)  \(extra)  [\(state)]");
    return true;
  }

  // ---------- marqueurs ----------

  private cb func OnSessionReady(event: ref<GameSessionEvent>) {
    ModLog(n"InkFlowProbe", "===== Session/Ready");
  }
  private cb func OnSessionEnd(event: ref<GameSessionEvent>) {
    ModLog(n"InkFlowProbe", "===== Session/BeforeEnd");
  }
  private cb func OnKey(event: ref<KeyInputEvent>) {
    if NotEquals(event.GetAction(), EInputAction.IACT_Press) { return; }
    this.marks += 1;
    ModLog(n"InkFlowProbe", s"===== MARK \(this.marks) (F9)");
  }
}
