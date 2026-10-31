# E-Presso Project Reflection

For this project, we built a Streamlit business intelligence application
that analyzes E-Presso revenue. We used ChatGPT to help plan the
application, explain unfamiliar programming concepts, generate Python
code, and troubleshoot errors. We also connected Google Gemini so users
could ask business questions through the application. Gemini selects
from approved analytical functions, while Python calculates the numerical
results.

We worked together throughout the process. Maci retrieved Power BI
information and helped guide the steps and comparisons. Makinlee entered
and ran the code, operated the application, performed tests, and saved
the project files and evidence. Because we were learning unfamiliar
tools, working in small stages made the project more manageable.

One significant challenge was separating correct calculations from
incorrect AI explanations. The assistant sometimes returned accurate
yearly revenue totals but incorrectly said that other sales channels
were excluded. We checked the dashboard filters and tool-call logs,
which showed that both channels were included. We revised the
instructions and added checks for misleading wording. Python now
supplies a statement describing the channel filter. A retest produced
the correct interpretation.

We also encountered connection failures and timeouts when using
Gemini. The application therefore includes a clearly labeled
rules-based fallback. This allows supported calculations to remain
available when the model cannot respond. Another revision improved
the customer-satisfaction question: instead of giving only a vague
unsupported message, the assistant now explains why association
does not establish causation and identifies the limits of its tools.

AI helped us build and understand code, but it did not remove the need
for our judgment. We compared application results with Power BI,
checked a separate revenue calculation, and reviewed whether the
explanations matched the evidence. We also increased one sales value
by exactly $1,000 and confirmed that the dashboard and assistant
responded to the changed data without code edits or restarting.

We would use this application to explore revenue patterns, but we would
not rely on it alone for major business decisions. Revenue does not
establish profit, and the current tools do not analyze the relationship
between satisfaction and sales. Real business use would require stronger
data validation, access controls, monitoring, and review by someone who
understands the business. This project showed us that a useful AI
application needs accurate calculations, visible evidence, clear
limitations, and human review.