# agents

## To run
add CREATEAI_API_KEY and CREATEAI_API_URL to .env file
```bash
CREATEAI_API_KEY=your_api_key
CREATEAI_API_URL=your_api_url
```

## Then run

```bash
python main.py
```

You can modify the config.json to change the workflow and the prompt can be added in main.py.

## Agent Architecture

<details open>
<summary>View Architecture Diagram</summary>

<svg width="100%" viewBox="0 0 680 1460" xmlns="http://www.w3.org/2000/svg" style="font-family: sans-serif; background: white;">
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <style>
    text { font-family: sans-serif; fill: #2C2C2A; }
    .th  { font-size: 14px; font-weight: 500; }
    .ts  { font-size: 12px; font-weight: 400; fill: #5F5E5A; }
    .arr { stroke: #888780; stroke-width: 1.5; fill: none; }
    .leader { stroke: #B4B2A9; stroke-width: 0.5; fill: none; }

    /* purple – agent/endpoint */
    .c-purple rect  { fill: #EEEDFE; stroke: #534AB7; }
    .c-purple .th   { fill: #3C3489; }
    .c-purple .ts   { fill: #534AB7; }

    /* blue – /query */
    .c-blue rect    { fill: #E6F1FB; stroke: #185FA5; }
    .c-blue .th     { fill: #0C447C; }
    .c-blue .ts     { fill: #185FA5; }

    /* coral – tools */
    .c-coral rect   { fill: #FAECE7; stroke: #993C1D; }
    .c-coral .th    { fill: #712B13; }
    .c-coral .ts    { fill: #993C1D; }

    /* teal – MCP / context */
    .c-teal rect    { fill: #E1F5EE; stroke: #0F6E56; }
    .c-teal .th     { fill: #085041; }
    .c-teal .ts     { fill: #0F6E56; }

    /* amber – file / storage */
    .c-amber rect   { fill: #FAEEDA; stroke: #854F0B; }
    .c-amber .th    { fill: #633806; }
    .c-amber .ts    { fill: #854F0B; }

    /* gray – neutral */
    .c-gray rect    { fill: #F1EFE8; stroke: #5F5E5A; }
    .c-gray .th     { fill: #444441; }
    .c-gray .ts     { fill: #5F5E5A; }

    /* red – abort/error */
    .c-red rect     { fill: #FCEBEB; stroke: #A32D2D; }
    .c-red .th      { fill: #791F1F; }
    .c-red .ts      { fill: #A32D2D; }
  </style>
</defs>

<!-- ROW 1: USER -->
<g class="c-gray">
  <rect x="240" y="24" width="200" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="39" text-anchor="middle" dominant-baseline="central">User</text>
  <text class="ts" x="340" y="57" text-anchor="middle" dominant-baseline="central">query + optional file upload</text>
</g>

<!-- FILE PROCESSOR branch -->
<path d="M240 46 L160 46 L160 108" fill="none" stroke="#888780" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>

<g class="c-amber">
  <rect x="60" y="108" width="160" height="68" rx="8" stroke-width="0.5"/>
  <text class="th" x="140" y="130" text-anchor="middle" dominant-baseline="central">File processor</text>
  <text class="ts" x="140" y="148" text-anchor="middle" dominant-baseline="central">any file → text + S3</text>
  <text class="ts" x="140" y="164" text-anchor="middle" dominant-baseline="central">stores raw + metadata</text>
</g>

<path d="M220 142 L260 142" fill="none" stroke="#BA7517" stroke-width="1" marker-end="url(#arrow)"/>
<g class="c-amber">
  <rect x="260" y="120" width="120" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="320" y="137" text-anchor="middle" dominant-baseline="central">S3</text>
  <text class="ts" x="320" y="153" text-anchor="middle" dominant-baseline="central">raw file + metadata</text>
</g>

<path d="M140 176 L140 216" fill="none" stroke="#BA7517" stroke-width="1" marker-end="url(#arrow)"/>
<g class="c-amber">
  <rect x="60" y="216" width="160" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="140" y="234" text-anchor="middle" dominant-baseline="central">Knowledge base</text>
  <text class="ts" x="140" y="250" text-anchor="middle" dominant-baseline="central">text version indexed</text>
</g>

<!-- /agents endpoint -->
<line x1="340" y1="68" x2="340" y2="108" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>

<g class="c-purple">
  <rect x="390" y="108" width="250" height="68" rx="8" stroke-width="0.5"/>
  <text class="th" x="515" y="130" text-anchor="middle" dominant-baseline="central">/agents endpoint</text>
  <text class="ts" x="515" y="148" text-anchor="middle" dominant-baseline="central">auth · rate limit · logging</text>
  <text class="ts" x="515" y="164" text-anchor="middle" dominant-baseline="central">scale · execution context</text>
</g>

<path d="M640 142 L660 142 L660 214 L540 214" fill="none" stroke="#534AB7" stroke-width="1" marker-end="url(#arrow)"/>
<g class="c-gray">
  <rect x="540" y="186" width="120" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="600" y="208" text-anchor="middle" dominant-baseline="central">DynamoDB</text>
  <text class="ts" x="600" y="226" text-anchor="middle" dominant-baseline="central">project config</text>
</g>

<text class="ts" x="390" y="198" fill="#5F5E5A">file metadata only</text>
<text class="ts" x="390" y="212" fill="#5F5E5A">(no raw file passed)</text>

<line x1="340" y1="176" x2="340" y2="216" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>

<!-- /query endpoint -->
<g class="c-blue">
  <rect x="240" y="216" width="200" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="233" text-anchor="middle" dominant-baseline="central">/query endpoint</text>
  <text class="ts" x="340" y="249" text-anchor="middle" dominant-baseline="central">RAG · KB · LLM inference</text>
</g>

<path d="M440 238 L480 238" fill="none" stroke="#185FA5" stroke-width="1" marker-end="url(#arrow)"/>
<g class="c-blue">
  <rect x="480" y="216" width="140" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="550" y="236" text-anchor="middle" dominant-baseline="central">DynamoDB</text>
  <text class="ts" x="550" y="252" text-anchor="middle" dominant-baseline="central">auth · rate limits</text>
  <text class="ts" x="550" y="265" text-anchor="middle" dominant-baseline="central">logs · model config</text>
</g>

<line x1="340" y1="260" x2="340" y2="300" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>
<text class="ts" x="352" y="284" fill="#5F5E5A">LLM first response</text>

<!-- Orchestrator agent -->
<g class="c-purple">
  <rect x="190" y="300" width="300" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="320" text-anchor="middle" dominant-baseline="central">Orchestrator agent (project A)</text>
  <text class="ts" x="340" y="340" text-anchor="middle" dominant-baseline="central">sees query + file metadata · decides next action</text>
</g>

<g class="c-teal">
  <rect x="16" y="300" width="164" height="68" rx="8" stroke-width="0.5"/>
  <text class="th" x="98" y="320" text-anchor="middle" dominant-baseline="central">Execution context</text>
  <text class="ts" x="98" y="338" text-anchor="middle" dominant-baseline="central">exec_id · call_chain</text>
  <text class="ts" x="98" y="354" text-anchor="middle" dominant-baseline="central">depth · max_depth</text>
</g>
<line x1="180" y1="334" x2="190" y2="334" stroke="#B4B2A9" stroke-width="0.5" stroke-dasharray="4 3" fill="none"/>

<!-- Action decision -->
<line x1="340" y1="356" x2="340" y2="388" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>
<g class="c-gray">
  <rect x="220" y="388" width="240" height="36" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="406" text-anchor="middle" dominant-baseline="central">What action to take?</text>
</g>

<!-- Three branches -->
<path d="M260 424 L130 468" fill="none" stroke="#888780" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="424" x2="340" y2="468" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>
<path d="M420 424 L550 468" fill="none" stroke="#888780" stroke-width="1" marker-end="url(#arrow)"/>

<!-- Tools -->
<g class="c-coral">
  <rect x="40" y="468" width="180" height="100" rx="8" stroke-width="0.5"/>
  <text class="th" x="130" y="492" text-anchor="middle" dominant-baseline="central">Tools</text>
  <text class="ts" x="130" y="512" text-anchor="middle" dominant-baseline="central">Gmail · Drive · Outlook</text>
  <text class="ts" x="130" y="528" text-anchor="middle" dominant-baseline="central">web search</text>
  <text class="ts" x="130" y="544" text-anchor="middle" dominant-baseline="central">code interpreter</text>
  <text class="ts" x="130" y="560" text-anchor="middle" dominant-baseline="central">file tool (see below)</text>
</g>

<!-- Sub-agent -->
<g class="c-purple">
  <rect x="250" y="468" width="180" height="68" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="492" text-anchor="middle" dominant-baseline="central">Sub-agent call</text>
  <text class="ts" x="340" y="512" text-anchor="middle" dominant-baseline="central">another project</text>
  <text class="ts" x="340" y="528" text-anchor="middle" dominant-baseline="central">internal /agents call</text>
</g>

<!-- MCP -->
<g class="c-teal">
  <rect x="460" y="468" width="180" height="100" rx="8" stroke-width="0.5"/>
  <text class="th" x="550" y="492" text-anchor="middle" dominant-baseline="central">MCP servers</text>
  <text class="ts" x="550" y="512" text-anchor="middle" dominant-baseline="central">user-hosted</text>
  <text class="ts" x="550" y="528" text-anchor="middle" dominant-baseline="central">or external URLs</text>
  <text class="ts" x="550" y="544" text-anchor="middle" dominant-baseline="central">any MCP protocol</text>
  <text class="ts" x="550" y="560" text-anchor="middle" dominant-baseline="central">own tools + KB</text>
</g>

<!-- Sub-agent recursion -->
<line x1="340" y1="536" x2="340" y2="576" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>

<g class="c-amber">
  <rect x="210" y="576" width="260" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="596" text-anchor="middle" dominant-baseline="central">Cycle + depth check</text>
  <text class="ts" x="340" y="614" text-anchor="middle" dominant-baseline="central">project_id in call_chain? depth &gt;= max?</text>
</g>

<path d="M280 632 L200 672" fill="none" stroke="#BA7517" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M400 632 L480 672" fill="none" stroke="#BA7517" stroke-width="1" marker-end="url(#arrow)"/>

<g class="c-red">
  <rect x="400" y="672" width="180" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="490" y="690" text-anchor="middle" dominant-baseline="central">Abort</text>
  <text class="ts" x="490" y="706" text-anchor="middle" dominant-baseline="central">return error to parent</text>
</g>

<g class="c-purple">
  <rect x="80" y="672" width="220" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="190" y="692" text-anchor="middle" dominant-baseline="central">Sub-agent (project B)</text>
  <text class="ts" x="190" y="710" text-anchor="middle" dominant-baseline="central">appends to call_chain · depth+1</text>
</g>

<line x1="190" y1="728" x2="190" y2="768" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>

<g class="c-blue">
  <rect x="80" y="768" width="100" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="130" y="784" text-anchor="middle" dominant-baseline="central">/query</text>
  <text class="ts" x="130" y="800" text-anchor="middle" dominant-baseline="central">own KB · DDB</text>
</g>
<g class="c-coral">
  <rect x="190" y="768" width="100" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="240" y="784" text-anchor="middle" dominant-baseline="central">Tools</text>
  <text class="ts" x="240" y="800" text-anchor="middle" dominant-baseline="central">own tools</text>
</g>
<g class="c-teal">
  <rect x="300" y="768" width="80" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="784" text-anchor="middle" dominant-baseline="central">MCP</text>
  <text class="ts" x="340" y="800" text-anchor="middle" dominant-baseline="central">own MCP</text>
</g>

<path d="M190 812 L190 840" fill="none" stroke="#534AB7" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<g class="c-purple">
  <rect x="100" y="840" width="180" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="190" y="856" text-anchor="middle" dominant-baseline="central">Sub-agent (project C)</text>
  <text class="ts" x="190" y="872" text-anchor="middle" dominant-baseline="central">cycle check repeats...</text>
</g>

<!-- File tool decision -->
<path d="M130 568 L130 892 L340 892" fill="none" stroke="#993C1D" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<text class="ts" x="190" y="884" text-anchor="middle" fill="#993C1D">file tool invoked</text>
<line x1="340" y1="892" x2="340" y2="928" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>

<g class="c-amber">
  <rect x="190" y="928" width="300" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="942" text-anchor="middle" dominant-baseline="central">Agent file tool decision</text>
  <text class="ts" x="340" y="958" text-anchor="middle" dominant-baseline="central">reads metadata · infers intent from query</text>
</g>

<path d="M240 972 L130 1012" fill="none" stroke="#BA7517" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M320 972 L280 1012" fill="none" stroke="#BA7517" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M380 972 L420 1012" fill="none" stroke="#BA7517" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M460 972 L550 1012" fill="none" stroke="#BA7517" stroke-width="1" marker-end="url(#arrow)"/>

<g class="c-coral">
  <rect x="40" y="1012" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="120" y="1032" text-anchor="middle" dominant-baseline="central">Code interpreter</text>
  <text class="ts" x="120" y="1050" text-anchor="middle" dominant-baseline="central">csv · xlsx analysis</text>
</g>
<g class="c-coral">
  <rect x="210" y="1012" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="290" y="1032" text-anchor="middle" dominant-baseline="central">Load to context</text>
  <text class="ts" x="290" y="1050" text-anchor="middle" dominant-baseline="central">summary · simple Q&amp;A</text>
</g>
<g class="c-coral">
  <rect x="380" y="1012" width="120" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="440" y="1032" text-anchor="middle" dominant-baseline="central">PDF / vision</text>
  <text class="ts" x="440" y="1050" text-anchor="middle" dominant-baseline="central">extract · describe</text>
</g>
<g class="c-coral">
  <rect x="510" y="1012" width="130" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="575" y="1032" text-anchor="middle" dominant-baseline="central">Other tools</text>
  <text class="ts" x="575" y="1050" text-anchor="middle" dominant-baseline="central">audio · video · etc</text>
</g>

<path d="M120 1068 L120 1120 L340 1120" fill="none" stroke="#993C1D" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M290 1068 L290 1120" fill="none" stroke="#993C1D" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M440 1068 L440 1120" fill="none" stroke="#993C1D" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M575 1068 L575 1120 L340 1120" fill="none" stroke="#993C1D" stroke-width="1" marker-end="url(#arrow)"/>

<line x1="340" y1="1120" x2="340" y2="1148" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>

<g class="c-purple">
  <rect x="180" y="1148" width="320" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="1168" text-anchor="middle" dominant-baseline="central">Tool results → LLM</text>
  <text class="ts" x="340" y="1188" text-anchor="middle" dominant-baseline="central">agent synthesizes · may loop for more actions</text>
</g>

<line x1="340" y1="1204" x2="340" y2="1244" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>

<g class="c-gray">
  <rect x="200" y="1244" width="280" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="1266" text-anchor="middle" dominant-baseline="central">Final response → user</text>
</g>

<!-- Legend -->
<line x1="40" y1="1308" x2="640" y2="1308" stroke="#B4B2A9" stroke-width="0.5"/>
<g class="c-purple"><rect x="40" y="1322" width="10" height="10" rx="2" stroke-width="0.5"/></g>
<text class="ts" x="56" y="1332" fill="#5F5E5A">Agent / endpoint</text>
<g class="c-blue"><rect x="170" y="1322" width="10" height="10" rx="2" stroke-width="0.5"/></g>
<text class="ts" x="186" y="1332" fill="#5F5E5A">/query layer</text>
<g class="c-coral"><rect x="290" y="1322" width="10" height="10" rx="2" stroke-width="0.5"/></g>
<text class="ts" x="306" y="1332" fill="#5F5E5A">Tools</text>
<g class="c-teal"><rect x="370" y="1322" width="10" height="10" rx="2" stroke-width="0.5"/></g>
<text class="ts" x="386" y="1332" fill="#5F5E5A">MCP / context</text>
<g class="c-amber"><rect x="490" y="1322" width="10" height="10" rx="2" stroke-width="0.5"/></g>
<text class="ts" x="506" y="1332" fill="#5F5E5A">File / storage</text>
<g class="c-red"><rect x="40" y="1350" width="10" height="10" rx="2" stroke-width="0.5"/></g>
<text class="ts" x="56" y="1360" fill="#5F5E5A">Abort / error</text>
<text class="ts" x="170" y="1360" fill="#5F5E5A">- - -  conditional / optional path</text>
<text class="ts" x="420" y="1360" fill="#5F5E5A">——  main execution path</text>
</svg>


</details>