# Application description

## Stage

In progress...

The most basic functions are usable

## Objective

The project begins with a raw text input, which is first cleaned by removing all paragraph and line breaks. This clean text is then split into full-paragraph fragments, ensuring each ends with a period and stays under a maximum of 3,500 characters. Each of these fragments is translated from Spanish to English one by one using a free Google Translate interface, to avoid request limits. After translation, the fragments are reassembled into a complete text with no line or paragraph breaks. This processed text is then analyzed using OpenAI’s updated ChatCompletion API with the "deepseek-chat" model, following a specific prompt designed to extract key ideas from cited authors, as well as a detailed summary from the main narrator. The result of this analysis is stored and displayed as the final output.

## How to use

```python
app.py # is the source code to use the aplication with a very minimal, and poor at this moment, interface with flask.

main.py # is the source code to use the aplication directly with python.

```

Author: This field is used to enter the citation in the format (author, year) of the article being processed.

Section text: This field is used to enter the subtitle of the literature review section of the article.

Source text: The citation or excerpt from the article being processed.

API Key: This is the API Key for the DeepSeek model. Alternatively, another model compatible with the openai package can be used with minimal changes to the source code.

Raw text to processing: This is where the raw, unprocessed text is pasted directly using a simple copy+paste mechanism.

Processing result: This field delivers the final result of the processing. 

Additionally, if the repository was cloned, the output will be automatically saved at the end of the process in both .csv and .txt formats inside the "docs" folder.