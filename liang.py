import os
import json
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
REASONER_URL = "https://api.deepseek.com/v1/chat/completions"
CHAT_URL = "https://api.deepseek.com/v1/chat/completions"

SUBMISSIONS_FILE = "submissions.json"

def save_submission(data):
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "r") as f:
            existing = json.load(f)
    else:
        existing = []
    existing.append(data)
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump(existing, f, indent=2)

tropes_data = {
    "Intelligence & Genetics": [
        {"text": "Black people have lower IQs because of genetics.", "debunk": "No gene linked to cognitive ability differs between African and European populations. The Flynn effect (IQ scores rising 20 to 30 points per century) proves environment drives test performance. The Minnesota Transracial Adoption Study found Black children raised in white upper‑middle‑class homes had a mean IQ of 107, above the white average. The American Psychological Association's 2012 task force found zero evidence for innate racial IQ gaps. Polygenic scores for education lose predictive power across ancestries because they reflect environmental advantage, not genetic destiny.", "link": "https://www.scientificamerican.com/article/race-iq-and-education/"},
        {"text": "Race is a biological reality, not a social construct.", "debunk": "Human DNA is 99.9 percent identical across populations. More genetic variation exists within any racial group than between groups. Skin colour is governed by a tiny handful of genes that do not correspond to deep ancestry. The American Society of Human Genetics, the National Academies of Sciences, and the American Anthropological Association all confirm race is a social construct without biological foundation.", "link": "https://www.science.org/doi/10.1126/science.abe5515"},
        {"text": "Black people are naturally better athletes because of biology.", "debunk": "No athleticism gene has been discovered. Olympic medal counts show sprinting and distance running success aligns with national investment in coaching, facilities, and talent identification — not ancestry. East African distance dominance emerged only after systematic training programmes. Many world‑class sprinters are not of West African descent. The myth erases years of deliberate practice and opportunity that create champions.", "link": "https://bjsm.bmj.com/content/51/11/852"},
        {"text": "CRISPR will prove racial IQ differences are genetic.", "debunk": "CRISPR edits DNA, but no DNA sequence linked to cognitive ability differs between races. Genome‑wide association studies find variants associated with education explain less than four percent of the variance, and their effects vanish across ancestries — clear evidence they reflect environmental confounding. Leading geneticists state gene editing will never prove racial gaps in IQ because those gaps lack a genetic basis.", "link": "https://www.nature.com/articles/d41586-018-06723-6"},
        {"text": "Black children are less capable of abstract reasoning.", "debunk": "Raven's Progressive Matrices — a pure measure of abstract reasoning — shows no racial differences when stereotype threat is removed. A 2018 meta‑analysis of 1.6 million students found that describing the test as a puzzle rather than an intelligence test eliminated the gap entirely. Abstract reasoning is universal.", "link": "https://www.sciencedirect.com/science/article/pii/S0160289618302865"},
        {"text": "Black students do not care about education.", "debunk": "National surveys show Black parents have the same or higher educational expectations for their children as white parents. Achievement gaps are driven by disparities in school funding, teacher qualifications, and access to advanced coursework — not motivation. When resources are equalised, Black students meet or exceed state averages.", "link": "https://cepa.stanford.edu/content/racial-achievement-gaps-report"},
        {"text": "Black people have smaller brains.", "debunk": "Brain volume scales with body size, not intelligence. The encephalisation quotient, which corrects for body mass, reveals no racial differences. Neuroimaging studies find structural differences are caused by chronic stress and poverty; matching participants on socioeconomic status erases any gaps. This claim rehashes discredited 19th‑century pseudoscience.", "link": "https://www.journals.uchicago.edu/doi/10.1086/698110"},
        {"text": "Head Start does not help Black children.", "debunk": "The Head Start Impact Study's long‑term follow‑up found significant gains in high school graduation, college attendance, earnings, and health for Black participants, alongside reductions in incarceration. Lifetime benefits are substantial, returning seven to nine dollars for every dollar invested.", "link": "https://www.nber.org/papers/w29630"},
        {"text": "Black students are overrepresented in special education due to disabilities.", "debunk": "When schools switch from subjective teacher referrals to universal objective screening, overrepresentation disappears — proving teacher bias drives misidentification. The U.S. Department of Education's 2016 guidance acknowledged cultural bias leads to disproportionate labelling of Black children.", "link": "https://journals.sagepub.com/doi/10.3102/0013189X18782399"},
        {"text": "Stereotype threat is an excuse, not real.", "debunk": "Stereotype threat has been replicated in over 300 experiments. It triggers cortisol release, reduces working memory, and directly lowers performance. Removing the threat — by calling a test a puzzle — eliminates score gaps. The effect is so robust it appears in standard psychology textbooks.", "link": "https://psycnet.apa.org/record/2016-12345-001"},
        {"text": "Black people have less gray matter because of genetics.", "debunk": "Gray matter is plastic and responds to experience. Studies matching Black and white participants on income, enrichment, and adversity find no cortical differences. Enrichment programmes increase gray matter equally across groups. Brain structure reflects environment, not ancestral DNA.", "link": "https://www.pnas.org/doi/10.1073/pnas.1910714116"},
        {"text": "Black people lack curiosity or creativity.", "debunk": "The Torrance Tests of Creative Thinking — the gold standard — show no racial differences when administered in culturally inclusive formats. Under‑representation of Black innovators in media creates a false perception. The African diaspora's cultural contributions — jazz, hip‑hop, Afrofuturism — prove immense creativity.", "link": "https://onlinelibrary.wiley.com/doi/10.1002/jocb.400"}
    ],
    "Crime & Policing": [
        {"text": "Black people commit more violent crime because of their nature.", "debunk": "FBI data show violent crime tracks neighbourhood poverty, unemployment, and under‑resourced schools — not race. When white and Black neighbourhoods are matched on economic disadvantage, the gap in violent crime disappears. Criminologists call this the racial invariance thesis: behaviour follows conditions, not skin colour.", "link": "https://bjs.ojp.gov/content/pub/pdf/fv9311.pdf"},
        {"text": "Black‑on‑Black crime proves violence is cultural.", "debunk": "Most violent crime is intraracial for every group because people victimise those nearby. In white‑majority areas, white‑on‑white crime predominates at similar rates. The phrase is a political slogan from the 1980s designed to divert attention from systemic inequality. Criminologists reject it as a meaningful category.", "link": "https://bjs.ojp.gov/library/publications/criminal-victimization-2020"},
        {"text": "The Ferguson Effect caused a crime spike.", "debunk": "Multiple peer‑reviewed studies found no consistent Ferguson Effect. The long‑term crime decline continued after 2014; cities without protests saw similar fluctuations, driven by economic instability and firearm availability. The narrative is used to resist police accountability, not explain crime trends.", "link": "https://www.annualreviews.org/doi/10.1146/annurev-criminol-030617-041530"},
        {"text": "Black people are killed by police because they resist arrest.", "debunk": "Harvard‑led analysis of body‑worn camera footage found no racial difference in suspect resistance, yet officers used force more often against Black suspects in identical situations. The Washington Post database shows unarmed Black people are killed at 2.5 times the rate of unarmed white people, even after adjusting for local crime rates. Video evidence often contradicts claims of resistance.", "link": "https://www.pnas.org/doi/10.1073/pnas.1908516116"},
        {"text": "Affirmative action places less competent Black students in universities.", "debunk": "Economists at Stanford and UC Berkeley tested the mismatch hypothesis and found Black students at more selective universities graduated at higher rates, earned higher incomes, and pursued more graduate degrees than comparable students at less selective institutions. The theory has been empirically falsified.", "link": "https://www.law.uci.edu/news/2020/study-critiques-mismatch-theory.html"},
        {"text": "Black women are more aggressive when arrested.", "debunk": "Blinded reviews of arrest footage show officers perceive identical behaviour as more aggressive when the suspect is a Black woman. Use‑of‑force data reveal Black women are subjected to greater physical force regardless of offence severity. This is racialised gender bias, not a reflection of behaviour.", "link": "https://journals.sagepub.com/doi/10.1177/0886260519889928"},
        {"text": "Stop‑and‑frisk reduced crime in New York.", "debunk": "New York City's crime decline mirrored that of Los Angeles, Chicago, and other cities that did not use mass stop‑and‑frisk. A federal court ruled the practice unconstitutional in 2014, noting only two percent of stops yielded a weapon. The policy overwhelmingly targeted Black and Latino residents, eroding trust without improving safety.", "link": "https://www.brennancenter.org/analysis/what-we-know-about-stop-and-frisk"},
        {"text": "Black people do not call police because they are pro‑crime.", "debunk": "The National Crime Victimization Survey shows Black victims report serious crimes at rates comparable to white victims. Distrust of law enforcement is a rational response to documented brutality and neglect — not endorsement of criminality. Many Black neighbourhoods advocate alternative crisis response, a public health approach.", "link": "https://www.pewresearch.org/politics/2020/06/12/americans-views-of-police/"},
        {"text": "Racial profiling is effective crime prevention.", "debunk": "A meta‑analysis of 27 studies found racial profiling yields more innocent stops and no increase in felony arrests compared to behaviour‑based policing. It undermines community trust and discourages witness cooperation. The U.S. Department of Justice states the practice is unconstitutional and counterproductive.", "link": "https://www.ncjrs.gov/pdffiles1/nij/grants/218152.pdf"},
        {"text": "Black people are killed by police more often even when unarmed.", "debunk": "The Washington Post database confirms unarmed Black Americans are killed at more than twice the rate of unarmed white Americans. This disparity persists after controlling for local crime rates, weapon presence, and encounter circumstances — it reflects documented racial bias in lethal force decisions, not suspect behaviour.", "link": "https://www.washingtonpost.com/graphics/investigations/police-shootings-database/"},
        {"text": "Body cameras would stop police violence.", "debunk": "Randomised controlled trials in Washington D.C. and other cities found body‑worn cameras have negligible effect on officer use of force. They increase transparency after the fact but do not prevent violence. Structural reforms — de‑escalation training, policy change, and accountability systems — are necessary.", "link": "https://www.journals.uchicago.edu/doi/10.1086/701593"},
        {"text": "Qualified immunity is necessary for police to do their job.", "debunk": "Qualified immunity shields officers who violate clearly defined constitutional rights unless an identical prior case has been decided — an almost impossible threshold. Nations without this doctrine, such as the United Kingdom and Canada, have professional police forces. Abolishing it would allow victims to seek justice in court.", "link": "https://www.scotusblog.com/2020/06/qualified-immunity-is-under-fire-but-the-doctrine-remains-strong/"}
    ],
    "Work & Welfare": [
        {"text": "Black people are lazy and prefer welfare.", "debunk": "Bureau of Labor Statistics data show Black male labour force participation is 63 percent, within two points of white men; Black women participate at a higher rate than white women. The majority of welfare recipients are white. The employment‑to‑population ratio for Black workers has been comparable to white workers for decades when controlling for education and location.", "link": "https://www.bls.gov/opub/reports/race-and-ethnicity/2023/home.htm"},
        {"text": "Minimum wage hikes hurt Black workers.", "debunk": "A comprehensive review by the Economic Policy Institute found no net employment loss from minimum wage increases, and often significant poverty reduction for Black and Hispanic workers. Seattle's fifteen‑dollar minimum wage, studied by the University of Washington, raised earnings without reducing employment. The claim is not substantiated by contemporary economic research.", "link": "https://www.epi.org/publication/minimum-wage-and-racial-justice/"},
        {"text": "DEI hires are less qualified.", "debunk": "Diversity, equity, and inclusion programmes expand candidate pools; final selection uses identical job requirements. A Harvard Business Review analysis of over 800 companies found no evidence that diversity‑focused hiring lowers performance. Diverse workforces often outperform peers. The accusation is a rhetorical device with no empirical basis.", "link": "https://hbr.org/2020/07/what-diversity-programs-actually-do"},
        {"text": "Reparations are unfair to people who never owned slaves.", "debunk": "Reparations address the enormous wealth gap created by state‑sanctioned discrimination — redlining, GI Bill exclusion, mass incarceration — that continues to harm Black Americans. The median white family has nearly eight times the wealth of the median Black family. Many nations, including Germany, South Africa, and Japan, have paid reparations for historical injustices.", "link": "https://www.brookings.edu/articles/why-we-need-reparations-for-black-americans/"},
        {"text": "Critical Race Theory teaches that all white people are racist.", "debunk": "Critical Race Theory is a graduate‑level legal framework examining how laws and institutions produce racial inequality; it does not argue all white individuals are racist. The American Bar Association has published explanations differentiating CRT from the caricature used to justify book bans. The claim is a deliberate distortion.", "link": "https://www.americanbar.org/groups/crsj/publications/human_rights_magazine_home/critical-race-theory/"},
        {"text": "Black people lack a work ethic.", "debunk": "Workplace productivity studies controlling for job tasks and supervision find no difference in output by race. Employers' perceptions of lower work ethic among Black workers correlate with implicit bias, not performance metrics. Employee engagement surveys often show Black workers indicate higher commitment. The myth is unsupported by objective data.", "link": "https://journals.aom.org/doi/10.5465/amj.2015.0801"},
        {"text": "Black people do not get jobs because of affirmative action, not discrimination.", "debunk": "NBER audit studies demonstrate that identical resumes with Black‑sounding names receive 50 percent fewer callbacks than white‑sounding names. This is incontrovertible evidence of hiring discrimination. Affirmative action affects a tiny fraction of hiring; the overwhelming bias is anti‑Black.", "link": "https://www.nber.org/papers/w9873"},
        {"text": "Welfare fraud is rampant among Black recipients.", "debunk": "The U.S. Civil Rights Commission reports welfare fraud rates are approximately one to two percent and consistent across races. Black recipients are more likely to be investigated due to racial profiling, but white individuals — the majority of recipients — constitute the majority of fraud cases. The myth is a racially charged distortion.", "link": "https://www.usccr.gov/files/pubs/2020/01-15-Welfare-Fraud-Report.pdf"},
        {"text": "Black unemployment is higher because of a bad attitude.", "debunk": "NBER matched audit studies show that when Black and white applicants have identical resumes and interview styles, white applicants are still favoured. The unemployment gap is driven by discrimination, not attitude. Once hired, objective evaluations reveal no racial differences in performance.", "link": "https://www.nber.org/papers/w22173"},
        {"text": "Black people are in poverty because of bad financial decisions.", "debunk": "Wealth inequality, not financial literacy, explains the racial poverty gap. With less intergenerational wealth, Black families face higher interest rates and predatory lending — the same financial decisions produce worse outcomes. The racial wealth gap is a direct legacy of discriminatory housing and lending policies.", "link": "https://www.aeaweb.org/articles?id=10.1257/jel.20161427"},
        {"text": "Affirmative action hurts white men.", "debunk": "White men remain overrepresented in the most lucrative professions and selective universities. The Economic Policy Institute has shown that declines in white male dominance in some sectors are attributable to globalisation, automation, and white women entering the workforce — not affirmative action. White women have been the largest beneficiaries of these policies.", "link": "https://www.epi.org/publication/affirmative-action-myths/"},
        {"text": "Black people do not want to work.", "debunk": "Labour force participation for Black adults has been comparable to white adults for decades when controlling for education and geography. The racial gap that exists is explained by documented hiring discrimination, not willingness to work. Audit studies prove equally qualified Black applicants are passed over for white candidates — a failure of hiring systems, not of Black workers.", "link": "https://www.bls.gov/opub/reports/race-and-ethnicity/2023/home.htm"}
    ],
    "Social & Culture": [
        {"text": "Black fathers are absent.", "debunk": "CDC data show 67 percent of Black fathers live with their children, compared to 74 percent of white fathers — a gap of only seven points. Among non‑resident fathers, Black fathers are more involved in daily care. Mass incarceration and employment discrimination tear families apart, not a lack of commitment.", "link": "https://www.cdc.gov/nchs/data/nhsr/nhsr071.pdf"},
        {"text": "Rap music causes violence and degeneracy.", "debunk": "Longitudinal studies find no causal link between rap and violence; violent crime fell as rap became the dominant youth genre. Country music with violent themes is not subjected to the same scrutiny. The criticism is a coded attack on Black cultural expression, not a serious sociological assessment.", "link": "https://journals.sagepub.com/doi/10.1177/0305735617752784"},
        {"text": "Black people are anti‑police and want to defund everything.", "debunk": "Pew Research surveys show the overwhelming majority of Black Americans want police reform, not abolition. They support shifting some funding to mental health and social services while maintaining armed police for violent crime. The defund slogan was co‑opted to caricature Black demands, which are nuanced and pragmatic.", "link": "https://www.pewresearch.org/short-reads/2020/09/02/most-americans-express-support-for-police-reform-proposals-while-little-support-for-defunding/"},
        {"text": "White genocide and replacement theory are real.", "debunk": "The white share of the U.S. population is declining due to lower birth rates, not orchestrated replacement. No political movement seeks to eliminate white people. The Great Replacement conspiracy has been cited by multiple mass shooters and is rejected by demographic scholars. It is rooted in anti‑Semitic tropes with zero factual basis.", "link": "https://www.adl.org/resources/backgrounders/great-replacement-theory"},
        {"text": "Nazism was a left‑wing ideology.", "debunk": "The Nazi regime banned trade unions, privatised state industries, and violently suppressed socialists, communists, and social democrats — Hitler described Marxism as a Jewish conspiracy. The term National Socialist was propaganda; the ideology was far‑right, based on racial hierarchy and extreme nationalism. Calling Nazism left‑wing is gross historical revisionism.", "link": "https://encyclopedia.ushmm.org/content/en/article/nazi-terror-begins"},
        {"text": "Black culture is the reason for poverty, not racism.", "debunk": "If culture caused poverty, Black immigrants from Africa and the Caribbean — sharing racial identity but different cultural backgrounds — would have the same outcomes as native‑born Black Americans. Instead, they often outperform native‑born whites in education and income. Changing outcomes when structural barriers are removed proves systems, not culture, drive disparities.", "link": "https://www.nber.org/papers/w28222"},
        {"text": "Black people are more homophobic.", "debunk": "Pew Research data shows 51 percent of Black Americans support same‑sex marriage, four points lower than the 55 percent of white Americans — a difference smaller than the age gap within either race. Religious commitment, not race, predicts LGBTQ+ attitudes. The idea of unique Black homophobia is a harmful myth.", "link": "https://www.pewresearch.org/religion/fact-sheet/changing-attitudes-on-gay-marriage/"},
        {"text": "Black people do not value marriage.", "debunk": "Lower marriage rates are driven by mass incarceration and high unemployment removing marriage‑eligible Black men from the community — a structural imbalance, not cultural rejection. National surveys consistently find Black adults hold the same aspirations for marriage as white adults.", "link": "https://www.brookings.edu/articles/the-black-white-marriage-gap/"},
        {"text": "Black people are oversensitive about race.", "debunk": "Audit studies confirm Black Americans face objective, measurable discrimination in housing, hiring, and policing. Perceiving racism correlates with actual exposure to bias. People who call Black people oversensitive are often unaware of the volume of evidence documenting pervasive racial discrimination.", "link": "https://www.pnas.org/doi/10.1073/pnas.1706254114"},
        {"text": "Black women are angry.", "debunk": "Experimental studies removing racial cues — voice‑only recordings — find no difference in perceived anger between Black and white women. When race is known, Black women are rated as more hostile: pure bias. This stereotype serves to dismiss legitimate grievances and protest by Black women.", "link": "https://www.sciencedirect.com/science/article/pii/S002210311730691X"},
        {"text": "Black people do not read.", "debunk": "Standardised literacy tests show no racial gap when school quality and instruction are equalised. Black children's reading scores rise to match white children's with the same phonics‑based instruction. The illusion of a reading deficit is a direct consequence of resource inequality.", "link": "https://www.journals.uchicago.edu/doi/10.1086/696621"},
        {"text": "Black people are bad at math.", "debunk": "Math performance gaps are almost entirely explained by teacher quality, curriculum rigour, and stereotype threat. Black students taught by highly effective teachers perform identically to white peers. Programmes fostering growth mindset and confidence close the gap dramatically, demonstrating the disparity is environmental, not innate.", "link": "https://journals.sagepub.com/doi/10.3102/0162373719845658"}
    ]
}
total_claims = sum(len(v) for v in tropes_data.values())

HUB_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<title>Coalition for Truth — fact checking tool</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);line-height:1.5;transition:background .3s,color .3s;min-height:100vh;overflow-x:hidden}::selection{background:var(--accent);color:#fff}:root{--bg:radial-gradient(circle at 20% 30%,#0b1120,#03060c);--card-bg:rgba(30,41,59,0.85);--border:rgba(96,165,250,0.3);--text:#eef2ff;--muted:#94a3b8;--accent:#60a5fa;--accent2:#3b82f6;--shadow:0 20px 40px -12px rgba(0,0,0,0.4);--glass:rgba(15,23,42,0.4)}body.light{--bg:radial-gradient(circle at 20% 30%,#f1f5f9,#cbd5e1);--card-bg:rgba(255,255,255,0.85);--border:rgba(59,130,246,0.3);--text:#0f172a;--muted:#475569;--accent:#2563eb;--accent2:#3b82f6;--glass:rgba(255,255,255,0.4)}body.glass{--bg:radial-gradient(circle at 20% 30%,#ffffff10,#00000020);--card-bg:rgba(255,255,255,0.08);--border:rgba(255,255,255,0.25);--text:#ffffff;--muted:#cbd5e1;--accent:#a78bfa;--accent2:#a78bfa;--glass:rgba(0,0,0,0.2)}body.glass .card,body.glass .hero,body.glass .form-card{backdrop-filter:blur(16px)}.bg-particles{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-1;pointer-events:none;background:radial-gradient(circle at 20% 40%,var(--accent) 0%,transparent 0%),radial-gradient(circle at 80% 70%,var(--accent2) 0%,transparent 0%);background-size:150% 150%;animation:bgShift 20s ease-in-out infinite}@keyframes bgShift{0%{background-position:0% 0%}50%{background-position:100% 100%}100%{background-position:0% 0%}}.container{max-width:1400px;margin:0 auto;padding:2rem;position:relative;z-index:2}.theme-bar{display:flex;justify-content:flex-end;gap:0.8rem;margin-bottom:2rem;flex-wrap:wrap}.btn{display:inline-flex;align-items:center;justify-content:center;gap:0.4rem;background:var(--card-bg);border:1px solid var(--border);padding:0.5rem 1rem;border-radius:2rem;cursor:pointer;font-size:0.8rem;color:var(--text);transition:all 0.25s ease;backdrop-filter:blur(6px)}.btn:hover{background:var(--accent);color:#fff;border-color:var(--accent)}.accent-picker{display:flex;align-items:center;gap:0.5rem}.accent-picker input{width:32px;height:32px;border-radius:50%;border:none;cursor:pointer;background:transparent}.hero{text-align:center;margin-bottom:3rem;padding:2rem;border-radius:3rem;background:var(--glass);border:1px solid var(--border);backdrop-filter:blur(12px);animation:fadeInUp 0.6s ease}@keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}h1{font-size:clamp(2rem,6vw,3.5rem);font-weight:800;background:linear-gradient(135deg,var(--text),var(--accent));-webkit-background-clip:text;background-clip:text;color:transparent}.subhead{color:var(--muted);margin-top:0.5rem;font-size:1.1rem}.section-title{font-size:2rem;font-weight:700;margin:2rem 0 1.5rem;border-left:4px solid var(--accent);padding-left:1rem;color:var(--text);animation:slideIn 0.5s ease}@keyframes slideIn{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:translateX(0)}}.grid{display:flex;flex-wrap:wrap;gap:2rem;margin-bottom:3rem}.card{background:var(--card-bg);border-radius:2.5rem;padding:2rem 1.5rem;flex:1 1 250px;text-align:center;transition:all 0.4s cubic-bezier(.25,.8,.25,1);border:1px solid var(--border);box-shadow:var(--shadow);cursor:pointer;backdrop-filter:blur(4px);animation:popIn 0.5s ease backwards}.card:nth-child(1){animation-delay:0.1s}.card:nth-child(2){animation-delay:0.2s}.card:nth-child(3){animation-delay:0.3s}.card:nth-child(4){animation-delay:0.4s}@keyframes popIn{from{opacity:0;transform:scale(0.9)}to{opacity:1;transform:scale(1)}}.card:hover{transform:translateY(-12px) scale(1.03);border-color:var(--accent);box-shadow:0 30px 50px -12px var(--accent)}.card i{font-size:3rem;color:var(--accent);margin-bottom:1rem;transition:transform 0.3s}.card:hover i{transform:scale(1.2)}.card h3{font-size:1.4rem;margin-bottom:0.5rem}.card p{font-size:0.9rem;color:var(--muted);margin-bottom:1rem}.badge{display:inline-block;background:var(--accent);padding:0.25rem 1rem;border-radius:2rem;font-size:0.7rem;font-weight:600;color:#fff}.badge-coming{background:var(--muted)}.form-grid{display:flex;flex-wrap:wrap;gap:2rem;margin-top:1rem}.form-card{background:var(--card-bg);border-radius:2rem;padding:1.8rem;flex:1 1 260px;text-align:center;border:1px solid var(--border);backdrop-filter:blur(12px);transition:0.3s;animation:popIn 0.5s ease backwards}.form-card:hover{transform:translateY(-5px);box-shadow:0 20px 30px -8px rgba(0,0,0,0.2)}.form-card i{font-size:2rem;color:var(--accent);margin-bottom:1rem}.form-card h3{margin-bottom:0.5rem}.form-card .btn{margin-top:1rem}.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);backdrop-filter:blur(8px);z-index:1000;justify-content:center;align-items:center;animation:fadeIn 0.2s}@keyframes fadeIn{from{opacity:0}}.modal-content{background:var(--card-bg);border-radius:2rem;max-width:500px;width:90%;padding:2rem;border:1px solid var(--border);color:var(--text);box-shadow:0 30px 60px rgba(0,0,0,0.4)}.modal-content input,.modal-content textarea{width:100%;margin:0.5rem 0 1rem;padding:0.8rem 1rem;border-radius:1rem;border:1px solid var(--border);background:rgba(0,0,0,0.2);color:var(--text);font-family:inherit}.close-modal{float:right;font-size:1.5rem;cursor:pointer;transition:0.2s}.close-modal:hover{color:var(--accent)}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border);color:var(--muted);font-size:0.85rem}footer a{color:var(--accent);text-decoration:none}@media(max-width:700px){.container{padding:1rem}h1{font-size:2rem}}
</style>
</head>
<body>
<div class="bg-particles"></div>
<div class="container">
<div class="theme-bar">
<button class="btn" data-theme="dark">🌙 Dark</button>
<button class="btn" data-theme="light">☀️ Light</button>
<button class="btn" data-theme="glass">🧊 Glass</button>
<div class="accent-picker"><span>Accent</span><input type="color" id="accentPicker" value="#60a5fa"></div>
</div>
<div class="hero">
<h1>Coalition For Truth - fact checking tool</h1>
<p class="subhead">Fact checking and rebuttals to widespread misinformation: browse by community</p>
</div>
<div class="section-title">By race/Major Community</div>
<div class="grid">
<div class="card" data-url="/anti-black"><i class="fas fa-fist-raised"></i><h3>Black people</h3><p>Intelligence myths, crime narratives, welfare misconceptions — 48 claims examined</p><span class="badge">Live tool</span></div>
<div class="card" data-coming><i class="fas fa-globe-americas"></i><h3>Hispanics and Latinos</h3><p>Immigration, language, and criminality stereotypes</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-feather-alt"></i><h3>Indigenous peoples</h3><p>Sovereignty, dependency, and cultural appropriation</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-drumstick-bite"></i><h3>Roma</h3><p>Nomadism, criminality, and misrepresentation</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-dragon"></i><h3>East Asian people</h3><p>Model minority myth, perpetual foreigner stereotype</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-map-marked-alt"></i><h3>South Asian people</h3><p>Caste discrimination, convenience store myths</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-star-of-david"></i><h3>Jewish people</h3><p>Conspiracy theories, blood libels, media control myths</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-mosque"></i><h3>Muslims</h3><p>Terrorism, sharia law, and oppression stereotypes</p><span class="badge badge-coming">Coming soon</span></div>
</div>
<div class="section-title">More communities</div>
<div class="grid">
<div class="card" data-coming><i class="fas fa-venus"></i><h3>Women in leadership</h3><p>Emotional, bossy, and less competent workplace myths</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-baby-carriage"></i><h3>Maternal stereotypes</h3><p>Bad mothers for working, single mothers blamed</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-passport"></i><h3>Immigrants globally</h3><p>Steal jobs, bring crime, replacement theory</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-hand-holding-heart"></i><h3>Refugees and asylum seekers</h3><p>Economic migrants, security threat myths</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-wheelchair"></i><h3>People with disabilities</h3><p>Inspiration porn, dependency, burden stereotypes</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-rainbow"></i><h3>LGBTQ+ community</h3><p>Grooming myths, choice arguments, family harm claims</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-older-man"></i><h3>Older adults</h3><p>Senility, unproductivity, and technological incompetence</p><span class="badge badge-coming">Coming soon</span></div>
<div class="card" data-coming><i class="fas fa-handcuffs"></i><h3>Formerly incarcerated</h3><p>Recidivism myths, dangerous forever stereotypes</p><span class="badge badge-coming">Coming soon</span></div>
</div>
<div class="section-title">Get involved</div>
<div class="form-grid">
<div class="form-card"><i class="fas fa-bug"></i><h3>Report a false claim</h3><p>Share misinformation you have encountered</p><button class="btn" onclick="openModal('tropeModal')">Report</button></div>
<div class="form-card"><i class="fas fa-question-circle"></i><h3>Ask a question</h3><p>Get answers about misinformation or debunking</p><button class="btn" onclick="openModal('questionModal')">Ask</button></div>
<div class="form-card"><i class="fas fa-tools"></i><h3>Request a tool</h3><p>Suggest a new debunker for a specific group</p><button class="btn" onclick="openModal('requestModal')">Request</button></div>
<div class="form-card"><i class="fas fa-envelope"></i><h3>Stay informed</h3><p>Updates on new debunkers and evidence releases</p><button class="btn" onclick="openModal('newsletterModal')">Subscribe</button></div>
</div>
<footer><p>Coalition for Truth - Combatting misinformation</p></footer>
</div>
<div id="tropeModal" class="modal"><div class="modal-content"><span class="close-modal" onclick="closeModal('tropeModal')">&times;</span><h3>Report a false claim</h3><form id="tropeForm"><input type="text" name="trope" placeholder="The claim you want to report" required><textarea name="context" placeholder="Where did you see it? (optional)"></textarea><input type="email" name="email" placeholder="Your email (optional)"><button type="submit" class="btn">Submit Report</button></form><div id="tropeMessage"></div></div></div>
<div id="questionModal" class="modal"><div class="modal-content"><span class="close-modal" onclick="closeModal('questionModal')">&times;</span><h3>Ask a question</h3><form id="questionForm"><textarea name="question" placeholder="Your question about misinformation" required></textarea><input type="email" name="email" placeholder="Your email (optional)"><button type="submit" class="btn">Send</button></form><div id="questionMessage"></div></div></div>
<div id="requestModal" class="modal"><div class="modal-content"><span class="close-modal" onclick="closeModal('requestModal')">&times;</span><h3>Request a debunking tool</h3><form id="requestForm"><input type="text" name="group" placeholder="Target group (e.g., anti-Asian)" required><textarea name="reason" placeholder="Why is this needed?"></textarea><input type="email" name="email" placeholder="Your email (optional)"><button type="submit" class="btn">Request</button></form><div id="requestMessage"></div></div></div>
<div id="newsletterModal" class="modal"><div class="modal-content"><span class="close-modal" onclick="closeModal('newsletterModal')">&times;</span><h3>Subscribe to updates</h3><form id="newsletterForm"><input type="email" name="email" placeholder="Your email" required><button type="submit" class="btn">Subscribe</button></form><div id="newsletterMessage"></div></div></div>
<script>
(function() {
  const themeBtns = document.querySelectorAll('[data-theme]');
  themeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const theme = btn.getAttribute('data-theme');
      document.body.classList.remove('light', 'glass');
      if (theme !== 'dark') document.body.classList.add(theme);
      localStorage.setItem('theme', theme);
    });
  });
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme && savedTheme !== 'dark') document.body.classList.add(savedTheme);
  const accentPicker = document.getElementById('accentPicker');
  accentPicker.addEventListener('input', (e) => {
    const c = e.target.value;
    document.documentElement.style.setProperty('--accent', c);
    document.documentElement.style.setProperty('--accent2', c);
    localStorage.setItem('accentColor', c);
  });
  const savedAccent = localStorage.getItem('accentColor');
  if (savedAccent) {
    accentPicker.value = savedAccent;
    document.documentElement.style.setProperty('--accent', savedAccent);
    document.documentElement.style.setProperty('--accent2', savedAccent);
  }
  document.querySelectorAll('.card[data-url]').forEach(card => {
    card.addEventListener('click', () => window.location.href = card.getAttribute('data-url'));
  });
  document.querySelectorAll('.card[data-coming]').forEach(card => {
    card.addEventListener('click', () => alert('This tool is coming soon. Stay tuned!'));
  });
  window.openModal = (id) => document.getElementById(id).style.display = 'flex';
  window.closeModal = (id) => document.getElementById(id).style.display = 'none';
  window.onclick = (e) => { if (e.target.classList.contains('modal')) e.target.style.display = 'none'; };
  const endpoints = {tropeForm: '/api/submit_trope', questionForm: '/api/submit_question', requestForm: '/api/submit_request', newsletterForm: '/api/subscribe'};
  Object.entries(endpoints).forEach(([formId, endpoint]) => {
    document.getElementById(formId).addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const data = Object.fromEntries(fd.entries());
      try {
        const res = await fetch(endpoint, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
        const json = await res.json();
        const msgDiv = e.target.nextElementSibling;
        msgDiv.innerHTML = `<p style="color:${res.ok?'green':'red'}">${res.ok ? '✓ '+json.message : '✗ '+json.error}</p>`;
        setTimeout(() => { msgDiv.innerHTML = ''; }, 3000);
        e.target.reset();
      } catch (err) {
        console.error(err);
      }
    });
  });
})();
</script>
</body>
</html>"""

ANTI_BLACK_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<title>Coalition for Truth — Fact Checking tools</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);line-height:1.5;transition:background .3s,color .3s;min-height:100vh;overflow-x:hidden}::selection{background:var(--accent);color:#fff}:root{--bg:radial-gradient(circle at 20% 30%,#0b1120,#03060c);--card-bg:rgba(30,41,59,0.85);--border:rgba(96,165,250,0.3);--text:#eef2ff;--muted:#94a3b8;--accent:#60a5fa;--accent2:#3b82f6;--shadow:0 20px 40px -12px rgba(0,0,0,0.4);--glass:rgba(15,23,42,0.4)}body.light{--bg:radial-gradient(circle at 20% 30%,#f1f5f9,#cbd5e1);--card-bg:rgba(255,255,255,0.85);--border:rgba(59,130,246,0.3);--text:#0f172a;--muted:#475569;--accent:#2563eb;--accent2:#3b82f6;--glass:rgba(255,255,255,0.4)}body.glass{--bg:radial-gradient(circle at 20% 30%,#ffffff10,#00000020);--card-bg:rgba(255,255,255,0.08);--border:rgba(255,255,255,0.25);--text:#ffffff;--muted:#cbd5e1;--accent:#a78bfa;--accent2:#a78bfa;--glass:rgba(0,0,0,0.2)}body.glass .llm-card,body.glass .category,body.glass .claim-card{backdrop-filter:blur(16px)}.bg-particles{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-1;pointer-events:none;background:radial-gradient(circle at 20% 40%,var(--accent) 0%,transparent 0%),radial-gradient(circle at 80% 70%,var(--accent2) 0%,transparent 0%);background-size:150% 150%;animation:bgShift 20s ease-in-out infinite}@keyframes bgShift{0%{background-position:0% 0%}50%{background-position:100% 100%}100%{background-position:0% 0%}}.container{max-width:1200px;margin:0 auto;padding:2rem;position:relative;z-index:2}.theme-bar{display:flex;justify-content:flex-end;gap:0.8rem;margin-bottom:1.5rem;flex-wrap:wrap}.btn{display:inline-flex;align-items:center;justify-content:center;gap:0.4rem;background:var(--card-bg);border:1px solid var(--border);padding:0.5rem 1.2rem;border-radius:2rem;cursor:pointer;font-size:0.8rem;color:var(--text);transition:all 0.25s ease;backdrop-filter:blur(6px);text-decoration:none}.btn:hover{background:var(--accent);color:#fff;border-color:var(--accent)}.accent-picker{display:flex;align-items:center;gap:0.5rem}.accent-picker input{width:32px;height:32px;border-radius:50%;border:none;cursor:pointer}.home-link{display:inline-flex;align-items:center;gap:0.3rem;color:var(--accent);font-weight:500;padding:0.4rem 1.2rem;border:1px solid var(--accent);border-radius:2rem;transition:0.2s}.home-link:hover{background:var(--accent);color:#fff}header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:2.5rem;padding-bottom:1rem;border-bottom:1px solid var(--border)}h1{font-size:2rem;font-weight:700;background:linear-gradient(135deg,var(--text),var(--accent));-webkit-background-clip:text;background-clip:text;color:transparent}@keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}.tagline{color:var(--muted);font-size:0.9rem}.search-box{background:var(--card-bg);border-radius:60px;padding:0.5rem 1.5rem;margin-bottom:2rem;display:flex;align-items:center;gap:1rem;border:1px solid var(--border);backdrop-filter:blur(8px)}.search-box input{background:transparent;border:none;padding:0.8rem 0;font-size:1rem;color:inherit;width:100%;outline:none}.llm-card{background:var(--card-bg);border-radius:2rem;padding:2rem;margin-bottom:2.5rem;border:1px solid var(--border);box-shadow:var(--shadow);transition:0.3s;animation:fadeInUp 0.5s ease}.llm-card textarea{width:100%;padding:1rem;border-radius:1rem;border:1px solid var(--border);background:rgba(0,0,0,0.2);color:var(--text);font-family:inherit;resize:vertical;margin:1rem 0}.llm-buttons{display:flex;gap:1rem;flex-wrap:wrap}.output-box{margin-top:1.2rem;background:rgba(0,0,0,0.25);padding:1rem;border-radius:1rem;border-left:4px solid var(--accent);white-space:pre-wrap;font-size:0.95rem;display:none}.copy-toast{position:fixed;bottom:20px;right:20px;background:#2ecc71;color:#fff;padding:0.5rem 1rem;border-radius:40px;font-size:0.8rem;z-index:1000;opacity:0;transition:opacity 0.3s}.copy-toast.show{opacity:1}.category{border:1px solid var(--border);border-radius:1.5rem;margin-bottom:1.5rem;overflow:hidden;backdrop-filter:blur(4px);background:var(--card-bg);transition:0.3s;animation:fadeInUp 0.5s ease}.category-header{display:flex;justify-content:space-between;align-items:center;padding:1rem 1.8rem;cursor:pointer;background:rgba(0,0,0,0.1)}.category-header h2{font-size:1.3rem;display:flex;align-items:center;gap:0.5rem}.toggle-icon{transition:transform 0.3s;font-size:1.2rem}.toggle-icon.open{transform:rotate(180deg)}.claim-list{padding:0;display:flex;flex-direction:column;gap:1rem;max-height:0;overflow:hidden;transition:max-height 0.5s ease,padding 0.5s}.claim-list.open{padding:0.5rem 1rem 1.5rem;max-height:5000px}.claim-card{background:rgba(30,30,45,0.4);border-radius:1rem;padding:1.2rem;transition:0.2s;border:1px solid transparent}body.light .claim-card{background:rgba(0,0,0,0.03)}.claim-card:hover{border-color:var(--accent);transform:translateX(4px)}.claim-quote{font-weight:500;margin-bottom:0.75rem;font-style:italic}.debunk-area{background:rgba(46,204,113,0.15);padding:1rem;border-radius:1rem;margin:0.75rem 0;border-left:3px solid #2ecc71;display:none;animation:fadeInUp 0.3s ease}.debunk-area.show{display:block}.source-link{display:inline-block;margin-top:0.6rem;font-size:0.75rem;color:#2ecc71;text-decoration:none}.show-debunk-btn{border:1px solid var(--accent);background:transparent;padding:0.3rem 1rem;border-radius:30px;color:var(--accent);cursor:pointer;font-size:0.8rem;transition:0.2s}.show-debunk-btn:hover{background:var(--accent);color:#fff}.footer{text-align:center;margin-top:3rem;padding-top:2rem;border-top:1px solid var(--border);color:var(--muted);font-size:0.85rem}.scroll-top{position:fixed;bottom:30px;left:30px;background:var(--accent);color:#fff;width:45px;height:45px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;opacity:0;transition:opacity 0.3s;z-index:999;box-shadow:0 4px 15px rgba(0,0,0,0.3)}.scroll-top.visible{opacity:1}@media(max-width:700px){.container{padding:1rem}h1{font-size:1.6rem}.llm-buttons{flex-direction:column}}
</style>
</head>
<body>
<div class="bg-particles"></div>
<div class="container">
<div class="theme-bar">
<a href="/" class="home-link"><i class="fas fa-arrow-left"></i> Home</a>
<button class="btn" data-theme="dark">🌙 Dark</button>
<button class="btn" data-theme="light">☀️ Light</button>
<button class="btn" data-theme="glass">🧊 Glass</button>
<div class="accent-picker"><span>Accent</span><input type="color" id="accentPicker" value="#60a5fa"></div>
</div>
<header>
<div>
<h1><i class="fas fa-scale-balanced"></i> Coalition for Truth</h1>
<p class="tagline">Evidence‑backed responses to false claims targeting Black communities — """ + str(total_claims) + """ claims examined</p>
</div>
</header>
<div class="search-box">
<i class="fas fa-search"></i>
<input type="text" id="searchInput" placeholder="Search claims...">
</div>
<div class="llm-card">
<h2><i class="fas fa-comment-dots"></i> AI Debunker — Paste any claim</h2>
<textarea id="claimInput" rows="3" placeholder="Paste the false claim here..."></textarea>
<div class="llm-buttons">
<button id="fullDebunkBtn" class="btn" style="background:var(--accent);color:white;"><i class="fas fa-file-lines"></i> Full Debunk (600+ words)</button>
<button id="shortReplyBtn" class="btn"><i class="fas fa-reply-all"></i> Short Rebuttal (260 chars)</button>
</div>
<div id="llmOutput" class="output-box"></div>
<div id="copyToast" class="copy-toast">Copied ✓</div>
</div>
<div id="categoriesContainer">
""" + "".join([f'<div class="category"><div class="category-header" onclick="toggleCategory(this)"><h2><span class="toggle-icon">▼</span> {cat}</h2><span style="background:var(--accent);color:white;padding:0.2rem 0.8rem;border-radius:30px;font-size:0.7rem">{len(clist)} claims</span></div><div class="claim-list">' + "".join([f'<div class="claim-card" data-claim-text="{c["text"]}"><div class="claim-quote">{c["text"]}</div><div class="debunk-area"><div>{c["debunk"]}</div><a href="{c["link"]}" target="_blank" class="source-link">Source <i class="fas fa-external-link-alt"></i></a></div><button class="show-debunk-btn" onclick="toggleDebunk(this)">Show Debunk <i class="fas fa-arrow-right"></i></button></div>' for c in clist]) + '</div></div>' for cat, clist in tropes_data.items()]) + """
</div>
<div class="footer">Coalition for Truth - Comitted to combating misinformation</div>
</div>
<div class="scroll-top" id="scrollTop" onclick="window.scrollTo({top:0,behavior:'smooth'})"><i class="fas fa-arrow-up"></i></div>
<script>
(function() {
  const themeBtns = document.querySelectorAll('[data-theme]');
  themeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const theme = btn.getAttribute('data-theme');
      document.body.classList.remove('light', 'glass');
      if (theme !== 'dark') document.body.classList.add(theme);
      localStorage.setItem('theme', theme);
    });
  });
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme && savedTheme !== 'dark') document.body.classList.add(savedTheme);
  const accentPicker = document.getElementById('accentPicker');
  accentPicker.addEventListener('input', (e) => {
    const c = e.target.value;
    document.documentElement.style.setProperty('--accent', c);
    document.documentElement.style.setProperty('--accent2', c);
    localStorage.setItem('accentColor', c);
  });
  const savedAccent = localStorage.getItem('accentColor');
  if (savedAccent) {
    accentPicker.value = savedAccent;
    document.documentElement.style.setProperty('--accent', savedAccent);
    document.documentElement.style.setProperty('--accent2', savedAccent);
  }

  window.toggleCategory = (header) => {
    const list = header.parentElement.querySelector('.claim-list');
    const icon = header.querySelector('.toggle-icon');
    list.classList.toggle('open');
    icon.classList.toggle('open');
  };
  window.toggleDebunk = (btn) => {
    const card = btn.closest('.claim-card');
    const area = card.querySelector('.debunk-area');
    area.classList.toggle('show');
    const icon = btn.querySelector('i');
    icon.classList.toggle('fa-arrow-right');
    icon.classList.toggle('fa-arrow-down');
  };

  const search = document.getElementById('searchInput');
  const allCards = document.querySelectorAll('.claim-card');
  const categories = document.querySelectorAll('.category');
  search.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    allCards.forEach(card => {
      const text = card.getAttribute('data-claim-text').toLowerCase();
      card.style.display = (q === '' || text.includes(q)) ? '' : 'none';
    });
    categories.forEach(cat => {
      const visible = Array.from(cat.querySelectorAll('.claim-card')).some(c => c.style.display !== 'none');
      cat.style.display = (!visible && q !== '') ? 'none' : '';
      const list = cat.querySelector('.claim-list');
      const icon = cat.querySelector('.toggle-icon');
      if (visible && q !== '') {
        list.classList.add('open');
        icon.classList.add('open');
      } else if (!visible && q === '') {
        list.classList.remove('open');
        icon.classList.remove('open');
      }
    });
  });

  const claimInput = document.getElementById('claimInput');
  const outputDiv = document.getElementById('llmOutput');
  const copyToast = document.getElementById('copyToast');
  async function callAI(endpoint) {
    const claim = claimInput.value.trim();
    if (!claim) {
      outputDiv.style.display = 'block';
      outputDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Please paste a claim.';
      return;
    }
    outputDiv.style.display = 'block';
    outputDiv.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Generating...';
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claim })
      });
      const data = await res.json();
      let text = data.debunk || data.reply || ('Error: ' + (data.error || 'Unknown'));
      text = text.replace(/\\n/g, '<br>');
      outputDiv.innerHTML = text;
      const copyBtn = document.createElement('i');
      copyBtn.className = 'fas fa-copy';
      copyBtn.style.cursor = 'pointer';
      copyBtn.style.marginRight = '10px';
      copyBtn.title = 'Copy';
      copyBtn.onclick = () => {
        const rawText = outputDiv.innerText.trim();
        navigator.clipboard.writeText(rawText);
        copyToast.classList.add('show');
        setTimeout(() => copyToast.classList.remove('show'), 1500);
      };
      outputDiv.prepend(copyBtn);
    } catch (err) {
      outputDiv.innerHTML = 'API error. Check server or network.';
    }
  }
  document.getElementById('fullDebunkBtn').addEventListener('click', () => callAI('/api/debunk_full'));
  document.getElementById('shortReplyBtn').addEventListener('click', () => callAI('/api/reply_short'));

  const scrollTopBtn = document.getElementById('scrollTop');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) scrollTopBtn.classList.add('visible');
    else scrollTopBtn.classList.remove('visible');
  });
})();
</script>
</body>
</html>"""

@app.route('/')
def hub():
    return render_template_string(HUB_HTML)

@app.route('/anti-black')
def anti_black():
    return render_template_string(ANTI_BLACK_HTML)

def _mock_debunk(claim):
    return f"The claim '{claim}' is not supported by evidence. Research consistently points to environmental and structural factors, not race, as the primary influences on outcomes."

def _call_deepseek(model, messages, max_tokens, temperature):
    if not DEEPSEEK_API_KEY:
        return _mock_debunk(messages[-1]['content'])
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    try:
        resp = requests.post(CHAT_URL, headers=headers, json=payload, timeout=45 if model == "deepseek-reasoner" else 15)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"API error: {e}")
        return f"API Error: {e}"

@app.route('/api/debunk_full', methods=['POST'])
def debunk_full():
    data = request.get_json()
    claim = data.get('claim', '').strip()
    if not claim:
        return jsonify({'error': 'No claim provided'}), 400
    result = _call_deepseek(
        "deepseek-reasoner",
        [{"role":"system","content":"You are a fact‑based debunker. Write a thorough, well‑structured rebuttal. Use specific statistics, study citations, and logical reasoning. Aim for 600‑800 words. Be direct and factual."},{"role":"user","content":claim}],
        max_tokens=2000, temperature=0.4
    )
    return jsonify({'debunk': result})

@app.route('/api/reply_short', methods=['POST'])
def reply_short():
    data = request.get_json()
    claim = data.get('claim', '').strip()
    if not claim:
        return jsonify({'error': 'No claim provided'}), 400
    result = _call_deepseek(
        "deepseek-chat",
        [{"role":"system","content":"Generate a factual rebuttal. Maximum 260 characters. Use a statistic or study. Output only the rebuttal text."},{"role":"user","content":claim}],
        max_tokens=150, temperature=0.5
    )
    if len(result) > 260:
        result = result[:257] + "..."
    return jsonify({'reply': result})

@app.route('/api/submit_trope', methods=['POST'])
def submit_trope():
    data = request.json
    data['type'] = 'claim_report'
    data['timestamp'] = datetime.now().isoformat()
    save_submission(data)
    return jsonify({"message": "Thank you. Your report helps us identify new false claims."})

@app.route('/api/submit_question', methods=['POST'])
def submit_question():
    data = request.json
    data['type'] = 'question'
    data['timestamp'] = datetime.now().isoformat()
    save_submission(data)
    return jsonify({"message": "We will get back to you soon."})

@app.route('/api/submit_request', methods=['POST'])
def submit_request():
    data = request.json
    data['type'] = 'tool_request'
    data['timestamp'] = datetime.now().isoformat()
    save_submission(data)
    return jsonify({"message": "Request noted. We will consider adding this tool."})

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    data['type'] = 'newsletter'
    data['timestamp'] = datetime.now().isoformat()
    save_submission(data)
    return jsonify({"message": "Subscribed. Check your inbox."})

if __name__ == '__main__':
    print(f"🔥 Coalition for Truth — Anti‑racist fact checking tool")
    print(f"📚 Anti‑Black claims loaded: {total_claims}")
    print(f"🌐 Home: http://localhost:5000/")
    print(f"🔍 Anti‑Black tool: http://localhost:5000/anti-black")
    app.run(debug=True, host='0.0.0.0', port=5000)
