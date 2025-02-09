
## Functional Requirements

The startup aims to provide online conversational and basic French lessons to tourists, backpackers, and entrepreneurs. Agile development will be employed. The company seeks to balance cost and performance by leveraging LLM providers such as OpenAI, Anthropic, Google, Perplexity, and Deepseek.

An investment of approximately AUD$100,000 is allocated for SaaS infrastructure, preferably on Google Cloud Platform (GCP) due to existing in-house expertise.

## Assumptions

We assume a fully cloud-native service architecture can be implemented without owning any infrastructure.

We assume that GCP can provide end-to-end infrastructure, including the chosen LLM (Model Garden - Vertex AI).

## Data Strategy

Due to concerns about copyrighted material, all learning resources will be purchased, stored, and accessed within our database.

## Considerations

IBM Granite is being considered due to its open-source nature and traceable training data, which helps mitigate copyright issues and provides transparency into the model's workings. (https://huggingface.co/ibm-granite)

Deepseekv3 and Deepseek R1 are also being considered for their performance and cost-effectiveness. (https://huggingface.co/deepseek-ai)