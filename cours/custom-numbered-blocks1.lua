-- custom-numbered-blocks.lua
-- Environnements numérotés pour Quarto HTML

local counters = {
  proposition = 0,
  theorem = 0,
  example = 0,
  definition = 0,
  lemma = 0,
  corollary = 0,
  remark = 0,
  methode = 0,
  exercice = 0,
  solution = 0
}

local titles = {
  proposition = "Proposition",
  theorem = "Théorème",
  example = "Exemple",
  definition = "Définition",
  lemma = "Lemme",
  corollary = "Corollaire",
  remark = "Remarque",
  methode = "Méthode",
  exercice = "Exercice",
  solution = "Solution"
}

local function reset_counters()
  for k, _ in pairs(counters) do
    counters[k] = 0
  end
end

-- On mémorise le numéro de section courant
local current_section = 0

local function section_number()
  return current_section
end

-- Détection des titres de niveau 1
function Header(el)

  if el.level == 1 then
    current_section = current_section + 1
    reset_counters()
  end

  return el
end


local function make_block(kind, el)

  if counters[kind] == nil then
    return el
  end

  counters[kind] = counters[kind] + 1

  local number =
    tostring(section_number()) ..
    "." ..
    tostring(counters[kind])

  local title = titles[kind]

  -- Titre personnalisé éventuellement fourni
  local custom_title = nil

  if el.attributes then
    custom_title = el.attributes["title"]
  end

  local displayed_title

  if custom_title and custom_title ~= "" then
    displayed_title =
      title .. " " .. number .. " — " .. custom_title
  else
    displayed_title =
      title .. " " .. number
  end

  -- Création du titre
  local title_para = pandoc.Para({
    pandoc.Strong({
      pandoc.Str(displayed_title)
    })
  })

  -- Ajout d'une classe CSS spécifique
  local classes = {
    "custom-numbered-block",
    "custom-" .. kind
  }

  -- On conserve les autres classes éventuelles
  if el.classes then
    for _, class in ipairs(el.classes) do
      if class ~= kind then
        table.insert(classes, class)
      end
    end
  end

  local attributes = {}

  -- On conserve les attributs sauf "title"
  if el.attributes then
    for key, value in pairs(el.attributes) do
      if key ~= "title" then
        attributes[key] = value
      end
    end
  end

  return pandoc.Div(
    {
      title_para,
      table.unpack(el.content)
    },
    pandoc.Attr(
      "",
      classes,
      attributes
    )
  )
end


function Div(el)

  -- Récupération de la classe principale
  for _, class in ipairs(el.classes) do

    if titles[class] ~= nil then
      return make_block(class, el)
    end

  end

  return el
end


-- Initialisation
reset_counters()

return {
  {
    Header = Header,
    Div = Div
  }
}


local function avec_titre(div, titre)
  table.insert(div.content, 1,
    pandoc.Para({pandoc.Strong(pandoc.Str(titre))}))
  div.classes = pandoc.List({"custom-numbered-block"})
  return div
end

function Div(div)
  if div.classes:includes("exercise") then
    return avec_titre(div, "Exercice")
  elseif div.classes:includes("solution") then
    return avec_titre(div, "Solution")
  end
end
