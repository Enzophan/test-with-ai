import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: "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",
});

const completion = openai.chat.completions.create({
  model: "gpt-4o-mini",
  store: true,
  messages: [
    {"role": "user", "content": "write a haiku about ai"},
  ],
});

completion.then((result) => console.log(result.choices[0].message));