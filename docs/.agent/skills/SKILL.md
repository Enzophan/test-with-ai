---
name: quiz-generate
description: "Use this skill when user asks to generate, export quiz. Triggers on phrases like \"generate quiz\", \"export quiz\". Creates a new CSV file with the exact format and structure based on the \"Quiz.csv\" and \"Answers.csv\" templates."
---
 
When this skill is activated, copy or write exactly the content from the existing questions and answers.

## Steps to generate quiz:
1. Create a new CSV file named `Answers_skill.csv`.
2. Copy the header row from `Answers.csv` into `Answers_skill.csv`.
3. Read all questions from `text.txt` and record those questions to `Answers_skill.csv` by rules:
    - Get Question, add double quotation marks for each question, and write it to "Question text" column.
    - Generate an "Answer ID" with the same format as "Answer 1", with sequentially increasing numbers, and unique.
    - Record each answer to each question in the "Quiz Answer Description" column.
4. Create a new CSV file named `Quiz_skill.csv`.
5. Copy the header row from `Quiz.csv` into `Quiz_skill.csv`.
6. For each question in `text.txt`, write the question text, explanation, and correct answer to `Quiz_skill.csv` in the corresponding columns.
7. The correct answer ID, compare the value of "Correct Answer" with the `Answers_skill.csv` to obtain the "Answer ID" value and write that ID to the "Correct Answer ID" column of `Quiz_skill.csv`.
8. Ensure that the final CSV files are properly formatted and can be opened in spreadsheet software without issues.


## Example of the expected output:
### Answers_skill.csv
```
Question text,Answer ID,Quiz Answer Description,
"What is Quality assurance (QA)?",Answer 1,"Perceptual, conditional, and somewhat subjective attributes, and may be understood differently by different people.",
"What is Quality assurance (QA)?",Answer 2,"Any systematic process of checking to see whether a product or service being developed is meeting specified requirements",
"What is Quality assurance (QA)?",Answer 3,"Is a process of executing a program or application with the intent of finding software bugs",
"What is Quality assurance (QA)?",Answer 4,"Nothing above",
```
### Quiz_skill.csv
```
Question text,Explannation,Correct Answer ID, Correct Answer
"What is Quality assurance (QA)?","Quality assurance (QA) is a systematic process of checking to see whether a product or service being developed is meeting specified requirements. It involves conducting various tests and evaluations to ensure that the product or service meets the desired quality standards. QA is important to identify any defects or issues in the development process and rectify them before the final product is released to the market. It helps in ensuring customer satisfaction and maintaining the reputation of the organization.",Answer 2,"Any systematic process of checking to see whether a product or service being developed is meeting specified requirements"
```
