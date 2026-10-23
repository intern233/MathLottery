import Lean

open Lean

-- This file is maintained by the harness. Submitted modules are loaded as data,
-- with extension loading and initializer execution disabled.
unsafe def main (args : List String) : IO Unit := do
  let (modules, rest) := args.span (· != "--")
  let names := rest.drop 1
  if modules.isEmpty || names.isEmpty then
    throw <| IO.userError "Expected modules -- declaration names"
  initSearchPath (← findSysroot)
  withImportModules (modules.toArray.map fun m => { module := m.toName }) {} fun env => do
    let mut results := #[]
    for label in names do
      let name := label.toName
      let some info := env.find? name |
        throw <| IO.userError s!"Missing declaration: {label}"
      let .thmInfo _ := info |
        throw <| IO.userError s!"Not a theorem declaration: {label}"
      let some idx := env.getModuleIdxFor? name |
        throw <| IO.userError s!"Missing defining module: {label}"
      let mod := env.allImportedModuleNames[idx.toNat]!.toString
      unless modules.contains mod do
        throw <| IO.userError s!"Declaration is not in a submitted module: {label}"
      let axioms ← (collectAxioms name : CoreM (Array Name)).toIO'
        { fileName := "MathLotteryInspector", fileMap := default } { env }
      results := results.push <| Json.mkObj [
        ("name", toJson label), ("module", toJson mod),
        ("type", toJson (toString info.type)),
        ("axioms", toJson (axioms.map Name.toString))]
    IO.println (Json.arr results).compress
