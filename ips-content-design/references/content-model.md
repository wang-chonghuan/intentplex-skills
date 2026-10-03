# Content model

Read this when a page is produced from data or by a model more than once: product pages, profile pages, generated reports, any template filled per item. The content model is the agreement between the data, the generator (a prompt or a template), and the code that renders the page. Write it before the prompt. A prompt written first decides the fields by accident.

## Fields

Record every field in one table:

| Field | Purpose | Source | Form and length | Required | When missing | Must not contain |
|---|---|---|---|---|---|---|
| `verdict` | Answers the page's one question for this item | Written by the model from `features`, `pricing` | One sentence, at most 20 words | Yes | Page is not published | Numbers absent from the source fields; praise with no fact behind it |
| `price_from` | Lets the reader rule the item out quickly | Copied from the pricing table | Number, currency, period | No | Field and label are not rendered | Estimates |

How to fill each column:

- **Purpose**: the line in the priority guide this field serves. A field with no line there is cut.
- **Source**: either "copied from data" or "written by the model from fields ...". Copied values (prices, dates, counts, names, URLs) never pass through the model, because a model that retypes a number can change it.
- **Form and length**: hard limits, chosen from the layout and from how much the reader needs. Enforce them in code.
- **Required**: if a required field is missing, the page has nothing to answer with. Do not publish it.
- **When missing**: by default the field and its label are not rendered. The other options are hiding the whole block, or not publishing the page. Placeholder text, "N/A", "No data available", and sentences explaining the gap are not options.
- **Must not contain**: what the generator would otherwise add, such as numbers missing from the source data, claims about the reader, comparisons with items not in the data, hedges, generic praise, and internal names of data sources or pipelines.

## Generator prompt

Ask for the fields. Do not ask for a page.

- State the job story and the one question, so the model knows what each field is for.
- List each model-written field with its purpose, length limit, and must-not-contain list.
- Pass only the source data for this one item.
- Tell the model to return `null` for any field its data does not support. Say this explicitly: a model that is not allowed to return null will invent a value.
- Request structured output that matches the model (for example JSON), so that layout and missing-data handling stay in the renderer.
- Be careful with examples in the prompt. A single example's phrasing tends to appear on every generated page. If you include one, check the outputs for its wording.

## Checks

Code checks, which are exact and cheap, run on every output:

- Schema, types, and required fields.
- Length limits.
- Every number in a model-written field also appears in that item's source data.
- `null` fields are hidden in the rendered page.
- A short banned-phrase list, as a backstop only.

Reading checks, done by you or the user, run on a sample of real outputs before generating at scale:

- Take at least 10 items, chosen to include the ones with the least data. Items with rich data hide the problems.
- For each page, answer the one question from the first screen only, and run the deletion test on each field.
- Read the sample side by side. If most pages share the same sentence shapes or the same opening, readers will notice that before anything else. Fix it in the prompt, so the change reaches every page.
