from transformers import pipeline

# Load the model
paraphraser = pipeline("text2text-generation", model="google/flan-t5-xl")

# Generate rewritten content

content0 = "Summarize and expand on the following text by adding more details and creating a detailed, comprehensive narrative. Ensure the output is at least 200 words long: "
content1 = "Sunrisers Hyderabad\u2019s pace bowling coach James Franklin addresses a press conference ahead of an IPL match against Lucknow Super Giants, at Rajiv Gandhi International Cricket Stadium, in Hyderabad, on March 26, 2025 Ahead of the IPL 2025 clashagainst Lucknow Super Giants (LSG)at home on Thursday (March 27, 2025), Sunrisers Hyderabad (SRH) bowling coach James Franklin said that cricket fans could get a chance to witness a 300 run-mark this season. Last year\u2019s finalists, SRH almost touched the 300-run mark in the previous encounter when theyplayed Rajasthan Royalsat the Rajiv Gandhi International Stadium in Hyderabad. The searing display with the bat mesmerised the spectators as they scripted the story of a 250-plus run total yet again. With a swashbuckling performance on a show, SRH powered its way to 286/6 against the Rajasthan Royals. This was the fourth instance of SRH breezing past the 250-plus total in T20s, the highest by any side in the format. Before their outing on Sunday, SRH was tied with Surrey for the most 250-plus totals in T20s. Speaking ahead of the match, Franklin said that this time around, teams have touched the 230-240 run-mark already, so there are chances that we can witness a 300-run match as well in the upcoming days. \u201cI\u2019d never say never."
content = content0 + content1
rewritten = paraphraser(content, max_length=1000, truncation=True, num_return_sequences=1)
print(rewritten[0]['generated_text'])
