--|
-- emoji-direct.lua
-- Direct emoji detection and wrapping for LuaLaTeX
-- Processes all Str elements and wraps emoji with appropriate font commands
--|

local filter_name = 'emoji-direct'

--- Show debug log?
local show_log = true

--- The default emoji font
local default_emojifont = 'Noto Color Emoji'

--- The emoji font to use
local emojifont = nil
--- All used codepoints
local ucs_used = {}
--- The number of emoji characters found
local emoji_count = 0

local concat, insert = table.concat, table.insert

--- Shows a debug log.
local function log(fmt, ...)
  if not show_log then return end
  io.stderr:write(filter_name..": "..fmt:format(...).."\n")
end

--- Check if a Unicode codepoint is an emoji
-- This covers most common emoji ranges
-- Note: Excludes arrows (U+2190-21FF) as they're in regular fonts, not emoji fonts
local function is_emoji(uc)
  return (uc >= 0x1F300 and uc <= 0x1F9FF) or  -- Misc Symbols and Pictographs, Emoticons, Transport, etc.
         (uc >= 0x2600 and uc <= 0x27BF) or     -- Misc symbols
         (uc >= 0x2300 and uc <= 0x23FF) or     -- Misc Technical
         (uc >= 0x2B50 and uc <= 0x2B55) or     -- Stars
         (uc >= 0x1F600 and uc <= 0x1F64F) or   -- Emoticons
         (uc >= 0x1F680 and uc <= 0x1F6FF) or   -- Transport and Map
         (uc >= 0x1F900 and uc <= 0x1F9FF) or   -- Supplemental Symbols
         (uc >= 0x1FA70 and uc <= 0x1FAFF) or   -- Extended pictographs
         (uc == 0x2708) or (uc == 0x2705) or (uc == 0x274C)  -- Specific symbols
end

--- Process a string and split it into text and emoji parts
local function process_string(text)
  local result = {}
  local current_text = {}
  local in_emoji = false
  
  for p, uc in utf8.codes(text) do
    if is_emoji(uc) then
      -- If we were building regular text, flush it
      if #current_text > 0 then
        insert(result, pandoc.Str(concat(current_text)))
        current_text = {}
      end
      
      -- Track this emoji
      if not ucs_used[uc] then
        log("emoji character found: U+%04X", uc)
        ucs_used[uc] = true
        emoji_count = emoji_count + 1
      end
      
      -- Add the emoji wrapped in LaTeX command
      local emoji_char = utf8.char(uc)
      insert(result, pandoc.RawInline('latex', '\\panEmoji{'))
      insert(result, pandoc.Str(emoji_char))
      insert(result, pandoc.RawInline('latex', '}'))
    else
      -- Regular character, accumulate it
      insert(current_text, utf8.char(uc))
    end
  end
  
  -- Flush any remaining text
  if #current_text > 0 then
    insert(result, pandoc.Str(concat(current_text)))
  end
  
  return result
end

--- Gets the LaTeX prologue to define emoji font
local function get_prologue()
  if not next(ucs_used) then
    return nil
  end
  
  local fname = emojifont or default_emojifont
  local ucs_list = {}
  for uc in pairs(ucs_used) do
    insert(ucs_list, uc)
  end
  table.sort(ucs_list)
  
  local ucs_strings = {}
  for _, uc in ipairs(ucs_list) do
    insert(ucs_strings, ('"%X'):format(uc))
  end
  local dcrsrc = concat(ucs_strings, ',\n')
  
  return ([[
\makeatletter
\ifnum0\ifdefined\directlua\directlua{
  if ("\luaescapestring{\luatexbanner}"):match("LuaHBTeX") then tex.write("1") end
}\fi>\z@
  \setfontface\p@emoji@font{%s}[Renderer=HarfBuzz]
\else
  \@latex@error{You must use 'lualatex' engine to print emoji}
    {The compilation will be aborted.}
  \let\p@emoji@font\relax
\fi
\ifdefined\ltjdefcharrange
  \ltjdefcharrange{208}{
    %s}
  \ltjsetparameter{jacharange={-208}}
\fi
\newcommand*{\panEmoji}[1]{{\p@emoji@font#1}}
\makeatother
]]):format(fname, dcrsrc)
end

--- Read metadata
local function read_meta(meta)
  if meta.emojifont then
    if type(meta.emojifont) == 'table' and meta.emojifont.t == 'MetaInlines' then
      emojifont = pandoc.utils.stringify(meta.emojifont)
    elseif type(meta.emojifont) == 'string' then
      emojifont = meta.emojifont
    end
    log('emojifont set to: %s', emojifont or 'nil')
  end
end

--- Process Str elements
local function process_str(elem)
  if #elem.text == 0 then
    return elem
  end
  
  -- Check if there are any emoji in this string
  local has_emoji = false
  for p, uc in utf8.codes(elem.text) do
    if is_emoji(uc) then
      has_emoji = true
      break
    end
  end
  
  if not has_emoji then
    return elem
  end
  
  -- Process the string and return the result
  return process_string(elem.text)
end

--- Add prologue to document
local function add_prologue(doc)
  log("total unique emoji found: %d", emoji_count)
  local src = get_prologue()
  if src then
    insert(doc.blocks, 1, pandoc.RawBlock('latex', src))
    log("prologue successfully inserted")
  end
  return doc
end

---------------------------------------- the filter
if FORMAT == 'latex' then
  return {
    { Meta = read_meta },
    { Str = process_str },
    { Pandoc = add_prologue }
  }
else
  log("format '%s' is not supported", FORMAT)
end

