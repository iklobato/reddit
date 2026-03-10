# CSV Column Explanations

Below is a detailed explanation of each column in the expected CSV output. This will help ensure clarity and consistency when converting a JSON schema/specification into the required CSV format.

---

## 1. Section Title
- **What it is:**  
  A human-readable title that describes the object or section being documented.
- **Purpose:**  
  Helps users quickly identify the purpose or context of the object in the schema.
- **Example:**  
  `Snak Layout`, `snakFormat Object Layout`

---

## 2. Object Name
- **What it is:**  
  The exact name of the object as it appears in the JSON schema or specification.
- **Purpose:**  
  Provides a direct reference to the object for developers and implementers.
- **Example:**  
  `snak`, `snakFormat`, `controlbar`

---

## 3. Fields (Grouped)
- **What it is:**  
  A comma-separated list of all the field names (properties) defined for this object, in the order they appear in the schema.
- **Purpose:**  
  Gives a quick overview of the structure and required data for the object.
- **Example:**  
  `id, name, format, version, aspectRatio, previewUrl, playButtonUrl, autoPlay, controlbar, sessionTimeout, urls, themes, timelines`

---

## 4. JSON
- **What it is:**  
  The full JSON definition of the object, including all its fields, types, and constraints, formatted as a string and properly escaped for CSV.
- **Purpose:**  
  Provides a precise, machine-readable reference for the object’s structure, useful for developers and for automated processing.
- **Example:**  
  """
snak": {
    "id": { "type": "uuid", "required": true, "nullable": false },
    ...
}"

---

## 5. Schema Description
- **What it is:**  
  A detailed, human-readable description of the object and each of its fields. Each field should be described on a new line, using the format:  
  `objectName.fieldName    Description`
- **Purpose:**  
  Explains the meaning, usage, and constraints of each field, making the schema understandable to both technical and non-technical stakeholders.
- **Example:**  
  snak                        An object containing all details describing the Snak.
  snak.id                     The ID of the Snak.
  snak.name                   The name of the Snak.
  ...

---

## 6. Snak Type
- **What it is:**  
  The type of Snak, if specified in the schema (e.g., `Teaser`). If not applicable, leave blank.
- **Purpose:**  
  Indicates the category or variant of the object, which may affect its behavior or usage in the application.
- **Example:**  
  `Teaser`

---

## 7. Cue Type
- **What it is:**  
  The cue type associated with the object, if specified (e.g., `Pool`). If not applicable, leave blank.
- **Purpose:**  
  Provides additional classification or context for the object, often used for routing or display logic.
- **Example:**  
  `Pool`

---

## 8. How To Use
- **What it is:**  
  Any special instructions, usage notes, or implementation guidelines relevant to this object. If none, leave blank.
- **Purpose:**  
  Offers practical advice or caveats for developers, such as best practices, limitations, or integration tips.
- **Example:**  
  (Could be blank, or contain notes like “Use this object to configure the player’s control bar.”)

---

## Summary Table

| Column Name         | Description                                                                                  | Example Value(s)                                  |
|---------------------|---------------------------------------------------------------------------------------------|---------------------------------------------------|
| Section Title       | Human-readable title for the object/section                                                 | Snak Layout                                       |
| Object Name         | Name of the object as in the schema                                                         | snak                                              |
| Fields (Grouped)    | Comma-separated list of all field names for the object                                      | id, name, format, ...                             |
| JSON                | Full JSON definition of the object, escaped for CSV                                         | """snak": { ... }"                               |
| Schema Description  | Human-readable description of the object and each field, one per line                       | snak.id The ID of the Snak. ...                   |
| Snak Type           | The Snak type, if specified; otherwise blank                                                | Teaser                                            |
| Cue Type            | The cue type, if specified; otherwise blank                                                 | Pool                                              |
| How To Use          | Usage notes or instructions, if any; otherwise blank                                        | (blank or usage notes)                            |

---

# Prompt Instructions

You are given a JSON schema or specification describing objects and their fields.

Your task: Convert this JSON into a CSV file with the following columns, in this exact order:

Section Title, Object Name, Fields (Grouped), JSON, Schema Description, Snak Type, Cue Type, How To Use

Instructions:

1. For each top-level object or section in the JSON, create a new row in the CSV.
2. Column mapping:
   - Section Title: Human-readable title for the object/section (e.g., "Snak Layout").
   - Object Name: The object’s name as used in the schema (e.g., "snak").
   - Fields (Grouped): Comma-separated list of all field names for this object, in the order they appear in the JSON.
   - JSON: The JSON definition for this object, formatted as a string. Escape all double quotes as "" for CSV compatibility.
   - Schema Description: For each field, provide a description in the format:
     objectName.fieldName    Description
     (one per line, preserve line breaks).
   - Snak Type: If present in the schema, include the value; otherwise, leave blank.
   - Cue Type: If present in the schema, include the value; otherwise, leave blank.
   - How To Use: If usage notes are present, include them; otherwise, leave blank.

3. If a field is an object or array, list its fields in "Fields (Grouped)" and include its full JSON definition in "JSON".
4. If a field is optional, nullable, or has allowed values, include this in "Schema Description".
5. If the JSON contains nested objects, only create a new row for top-level objects. Reference nested objects in "JSON" and "Schema Description" as needed.
6. All columns must be present for every row, even if some are blank.
7. The CSV must:
   - Use UTF-8 encoding.
   - Use a comma (`,`) as the delimiter.
   - Enclose all fields in double quotes.
   - Escape double quotes inside fields as "".
   - Use LF (`\n`) for line endings.

Example Input:
```json
{
  "snak": {
    "id": { "type": "uuid", "required": true, "nullable": false },
    "name": { "type": "string", "required": true, "nullable": false }
  }
}
```

Example Output:
```
"Section Title","Object Name","Fields (Grouped)","JSON","Schema Description","Snak Type","Cue Type","How To Use"
"Snak Layout","snak","id, name","""snak": {
    ""id"": { ""type"": ""uuid"", ""required"": true, ""nullable"": false },
    ""name"": { ""type"": ""string"", ""required"": true, ""nullable"": false }
}","snak                        An object containing all details describing the Snak.
snak.id                     The ID of the Snak.
snak.name                   The name of the Snak.",,,
```

Process all objects in the JSON in this way.
If a field or value is missing, leave the corresponding column blank.
Do not omit any columns or rows.
Do not add extra commentary or explanation—output only the CSV.

Tips for Best Results:
- Be explicit about every step and format.
- Provide both input and output examples.
- Specify how to handle edge cases and missing data.
- Require strict adherence to the column order and formatting. 