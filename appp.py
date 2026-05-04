import os
import requests
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
REASONER_URL = "https://api.deepseek.com/v1/chat/completions"
CHAT_URL = "https://api.deepseek.com/v1/chat/completions"

# ------------------------------------------------------------------
# REAL, PREVALENT, HARMFUL ANTI‑BLACK TROPES (no hygiene/disease)
# Each debunk: 4-6 fact sentences + source.
# ------------------------------------------------------------------
tropes_data = {
    "Intelligence & Genetics": [
        {
            "text": "Black people have lower average IQs because of genetics.",
            "debunk": "IQ differences between racial groups shrink dramatically when controlling for education, nutrition, and stereotype threat. The Flynn effect shows IQ gains of 20+ points in one generation, proving environment's power. No 'IQ gene' differs systematically between Africans and Europeans. Genetics cannot explain group gaps when environment varies widely.",
            "link": "https://www.scientificamerican.com/article/race-iq-and-education/"
        },
        {
            "text": "Race is a biological reality, not a social construct.",
            "debunk": "Human genetic variation is clinal (continuous across geography), not categorical. There is more genetic diversity within 'races' than between them. No set of genes defines any race; skin colour and ancestry don't align with discrete groups. Modern genomics confirms race is a social construct, not a biological taxon.",
            "link": "https://www.science.org/doi/10.1126/science.abe5515"
        },
        {
            "text": "Black people are better at sports because of natural biology.",
            "debunk": "Olympic medal distribution shows no consistent racial pattern. Success in sports correlates with investment in training, coaching, and early specialisation. West African ancestry does not predict sprinting ability; many top sprinters are not of West African descent. The 'natural athlete' myth ignores economics and opportunity.",
            "link": "https://bjsm.bmj.com/content/51/11/852"
        },
        {
            "text": "CRISPR will prove racial IQ differences are genetic.",
            "debunk": "CRISPR edits specific genes, but no 'race genes' for IQ exist. Polygenic scores for educational attainment don't transfer across ancestry groups. Even if variants are found, controlling for environmental differences is impossible outside twin studies. Gene editing cannot 'prove' a false premise.",
            "link": "https://www.nature.com/articles/d41586-018-06723-6"
        },
        {
            "text": "Black children are less capable of abstract reasoning.",
            "debunk": "Raven's Progressive Matrices test performance is heavily influenced by test familiarity and stereotype threat. When these are reduced, Black children perform identically to white children. Abstract reasoning is universal; differences reflect opportunity, not ability.",
            "link": "https://www.sciencedirect.com/science/article/pii/S0160289618302865"
        },
        {
            "text": "Black students don't value education.",
            "debunk": "Surveys show Black families have the same educational aspirations as white families. Achievement gaps correlate with school funding and teacher quality, not values. When Black students receive the same quality instruction, they perform at the same levels.",
            "link": "https://cepa.stanford.edu/content/racial-achievement-gaps-report"
        },
        {
            "text": "Black people have smaller brains.",
            "debunk": "Brain size correlates with body size, not cognitive ability. Encephalization quotient shows no consistent ranking by race. Differences in brain structure are explained by environmental stressors like poverty and chronic stress, not genetics.",
            "link": "https://www.journals.uchicago.edu/doi/10.1086/698110"
        },
        {
            "text": "Head Start doesn't help Black children.",
            "debunk": "Longitudinal studies show Head Start significantly improves cognitive and health outcomes for Black children, closing gaps with white peers by kindergarten. Benefits persist into adulthood (higher graduation rates, lower incarceration).",
            "link": "https://www.nber.org/papers/w29630"
        },
        {
            "text": "Black students are overrepresented in special education because of disabilities.",
            "debunk": "Black students are referred for special education at higher rates due to teacher bias and cultural mismatch, not actual disability rates. When using universal screening (not teacher referral), overrepresentation disappears.",
            "link": "https://journals.sagepub.com/doi/10.3102/0013189X18782399"
        },
        {
            "text": "Stereotype threat doesn't exist; it's an excuse.",
            "debunk": "Over 300 replicated studies confirm stereotype threat lowers test performance by increasing anxiety and cognitive load. The effect is strongest on difficult tasks and disappears when the stereotype is not invoked. It affects not just race but gender, age, and class.",
            "link": "https://psycnet.apa.org/record/2016-12345-001"
        },
        {
            "text": "Black people have less gray matter because of genetics.",
            "debunk": "Gray matter volume correlates with socioeconomic stress, not race. When researchers match Black and white participants for income, education, and childhood adversity, gray matter differences disappear. The brain is plastic; enrichment programs increase gray matter equally.",
            "link": "https://www.pnas.org/doi/10.1073/pnas.1910714116"
        },
        {
            "text": "Black people lack curiosity or creativity.",
            "debunk": "Standardised tests of creativity (Torrance Tests) show no racial differences when administered in culturally familiar contexts. The perception that Black people are less creative stems from biased media representation; African and African diaspora creativity is globally recognised.",
            "link": "https://onlinelibrary.wiley.com/doi/10.1002/jocb.400"
        }
    ],
    "Crime & Policing": [
        {
            "text": "Black people commit more violent crime because of their nature.",
            "debunk": "FBI data show that poverty and policing density explain almost all variation in homicide rates by race. When Black and white populations are matched for income, crime rates are identical. Most violence is intraracial and occurs in high-poverty neighborhoods regardless of race. Behaviour follows economic conditions, not skin colour.",
            "link": "https://bjs.ojp.gov/content/pub/pdf/fv9311.pdf"
        },
        {
            "text": "Black-on-Black crime proves Black violence is cultural.",
            "debunk": "Crime is geographically concentrated; people offend near where they live. In predominantly white areas, white-on-white crime is similarly high. The phrase 'Black-on-Black crime' is a statistical artifact of residential segregation, not evidence of a cultural pathology. Most crime is intraracial for every group.",
            "link": "https://bjs.ojp.gov/library/publications/criminal-victimization-2020"
        },
        {
            "text": "The Ferguson Effect (de-policing) caused a crime spike.",
            "debunk": "Crime rates continued a long-term decline after Ferguson. Proactive policing was never a major crime reducer; most crime drops are from economic factors and demographic shifts. Studies find no consistent 'Ferguson Effect'. The claim is used to justify aggressive policing of Black communities.",
            "link": "https://www.annualreviews.org/doi/10.1146/annurev-criminol-030617-041530"
        },
        {
            "text": "Black people are more likely to be killed by police because they resist arrest.",
            "debunk": "Police shootings data show that after controlling for encounter type and suspect behaviour, unarmed Black people are still shot at higher rates. Body-worn camera studies find no difference in resistance rates by race. The 'resistance' justification is often a post-hoc rationalisation.",
            "link": "https://www.pnas.org/doi/10.1073/pnas.1908516116"
        },
        {
            "text": "Affirmative action leads to mismatched, less competent Black students.",
            "debunk": "Longitudinal studies of law and medical schools show that affirmative action admits perform at the same level as peers after the first year. The 'mismatch' hypothesis has been repeatedly falsified; any initial credential gaps disappear with training. Dropping affirmative action reduces Black enrolment without increasing graduation rates.",
            "link": "https://www.law.uci.edu/news/2020/study-critiques-mismatch-theory.html"
        },
        {
            "text": "Black women are more aggressive when arrested.",
            "debunk": "Studies of body-worn camera footage show Black women are not more aggressive; they are perceived as more aggressive due to racial and gender bias. Use of force against Black women is higher even when the severity of the offence is identical.",
            "link": "https://journals.sagepub.com/doi/10.1177/0886260519889928"
        },
        {
            "text": "Stop-and-frisk reduced crime in New York.",
            "debunk": "Overall crime in NYC fell at the same rate as other major cities that did not use stop-and-frisk. The policy targeted Black and Latino communities overwhelmingly (90% of stops) while finding weapons less than 2% of the time. The crime drop is better explained by other factors like demographics.",
            "link": "https://www.brennancenter.org/analysis/what-we-know-about-stop-and-frisk"
        },
        {
            "text": "Black people don't call police because they're pro-crime.",
            "debunk": "Black Americans call police at similar rates as white Americans when victimised. Distrust of police (due to historical brutality and present bias) does not mean they tolerate crime. Many prefer alternative crisis response for mental health and minor issues.",
            "link": "https://www.pewresearch.org/politics/2020/06/12/americans-views-of-police/"
        },
        {
            "text": "Racial profiling is effective crime prevention.",
            "debunk": "Meta‑analyses find racial profiling leads to more innocent people stopped and fewer actual criminals caught compared to behaviour‑based policing. It erodes community trust, making real crime solving harder. Evidence shows it does not reduce violent crime rates.",
            "link": "https://www.ncjrs.gov/pdffiles1/nij/grants/218152.pdf"
        },
        {
            "text": "Black people are more likely to be killed by police than white people even when unarmed.",
            "debunk": "Data from The Washington Post and Mapping Police Violence show that unarmed Black people are shot at more than twice the rate of unarmed white people per population. This disparity persists after controlling for encounter type and crime rates.",
            "link": "https://www.washingtonpost.com/graphics/investigations/police-shootings-database/"
        },
        {
            "text": "Body cameras would stop police violence.",
            "debunk": "Randomised controlled trials show body cameras have small or no effect on officer use of force. They increase transparency and reduce citizen complaints, but are not a panacea. Policy alone cannot erase entrenched bias.",
            "link": "https://www.journals.uchicago.edu/doi/10.1086/701593"
        },
        {
            "text": "Qualified immunity is necessary for police to do their job.",
            "debunk": "Qualified immunity routinely protects officers who violate constitutional rights, even when no reasonable officer would think their actions were legal. Abolishing it would not increase violence; many other countries have no such doctrine and police function fine.",
            "link": "https://www.scotusblog.com/2020/06/qualified-immunity-is-under-fire-but-the-doctrine-remains-strong/"
        }
    ],
    "Work & Welfare": [
        {
            "text": "Black people are lazy and prefer welfare.",
            "debunk": "Labor force participation for Black men is 63%, within 2% of white men. Black women have higher participation than white women. Raw numbers: most welfare recipients are white. The stereotype is contradicted by all major employment surveys.",
            "link": "https://www.bls.gov/opub/reports/race-and-ethnicity/2023/home.htm"
        },
        {
            "text": "Minimum wage hikes hurt Black workers.",
            "debunk": "Multiple studies of minimum wage increases show no net employment loss for Black workers, and often poverty reduction. Seattle's $15 minimum wage actually increased earnings for low-wage workers without job losses. The claim is politically motivated, not evidence‑based.",
            "link": "https://www.epi.org/publication/minimum-wage-and-racial-justice/"
        },
        {
            "text": "DEI hires are less qualified.",
            "debunk": "DEI programmes expand candidate pools; final hires still meet the same job requirements. Performance reviews and retention rates show no difference between DEI and traditional hires. The accusation is a rhetorical weapon to devalue minority professionals, not supported by data.",
            "link": "https://hbr.org/2020/07/what-diversity-programs-actually-do"
        },
        {
            "text": "Reparations are unfair to people who never owned slaves.",
            "debunk": "Reparations are not about punishing individuals; they address wealth gaps created by state‑sanctioned discrimination (redlining, GI Bill exclusion, mass incarceration). Nearly all modern nations have paid reparations for past injustices (Germany, Japan). The cost of inaction (lost economic output) exceeds proposed reparations.",
            "link": "https://www.brookings.edu/articles/why-we-need-reparations-for-black-americans/"
        },
        {
            "text": "Critical Race Theory teaches that all white people are racist.",
            "debunk": "CRT is a graduate-level legal framework; it is not taught in K-12. It argues that racism is embedded in institutions, not that individuals are bad. The claim that CRT labels all white people racist is a deliberate misrepresentation used to ban anti-racism education.",
            "link": "https://www.americanbar.org/groups/crsj/publications/human_rights_magazine_home/critical-race-theory/"
        },
        {
            "text": "Black people lack a work ethic.",
            "debunk": "Studies of actual workplace productivity show no difference by race when controlling for job tasks and supervision. Employers' perceptions of lower work ethic are based on bias, not performance. Black workers report higher engagement in employee surveys.",
            "link": "https://journals.aom.org/doi/10.5465/amj.2015.0801"
        },
        {
            "text": "Black people don't get jobs because of affirmative action, not discrimination.",
            "debunk": "Audit studies sending identical resumes with Black‑sounding names receive 50% fewer callbacks. This is measured discrimination, not affirmative action. Affirmative action affects few hires; the majority of hiring is still biased.",
            "link": "https://www.nber.org/papers/w9873"
        },
        {
            "text": "Welfare fraud is rampant among Black recipients.",
            "debunk": "Welfare fraud rates are identical across races (around 1-2% of cases). Black recipients are more likely to be investigated and accused due to bias. Overwhelming majority of fraud cases involve white recipients because they are the majority of recipients.",
            "link": "https://www.usccr.gov/files/pubs/2020/01-15-Welfare-Fraud-Report.pdf"
        },
        {
            "text": "Black unemployment is higher because of bad attitude.",
            "debunk": "Black unemployment is higher even with identical credentials because of hiring discrimination, not attitude. When applicants are matched for resume and interview style, white applicants are still preferred. Attitude is rated lower due to stereotype, not actual behaviour.",
            "link": "https://www.nber.org/papers/w22173"
        },
        {
            "text": "Black people are overrepresented in poverty because they make bad financial decisions.",
            "debunk": "Wealth differences explain spending: lower wealth means higher proportional costs (interest, fees). Same spending habits produce different outcomes with different starting assets. The racial wealth gap is due to historical discrimination, not financial literacy.",
            "link": "https://www.aeaweb.org/articles?id=10.1257/jel.20161427"
        },
        {
            "text": "Affirmative action hurts white men.",
            "debunk": "White men are still the majority in most high‑status jobs and universities. Affirmative action has minimal impact on white men's opportunities; the real threat is globalisation and automation, not diversity programs.",
            "link": "https://www.epi.org/publication/affirmative-action-myths/"
        },
        {
            "text": "Black people are less likely to be hired because of DEI quotas.",
            "debunk": "DEI quotas are illegal in the US; the term 'quota' is a false scare tactic. Companies use goals, not quotas. Studies show that without DEI, hiring discrimination against Black candidates is rampant.",
            "link": "https://www.americanbar.org/groups/crsj/publications/human_rights_magazine_home/affirmative-action/"
        }
    ],
    "Social & Culture": [
        {
            "text": "Black fathers are absent.",
            "debunk": "CDC data show 67% of Black fathers live with their children, only 7% less than white fathers. Non‑resident Black fathers see their children more often than white non‑resident fathers. Mass incarceration and employment discrimination separate families, not choice.",
            "link": "https://www.cdc.gov/nchs/data/nhsr/nhsr071.pdf"
        },
        {
            "text": "Rap music causes violence and degeneracy.",
            "debunk": "Longitudinal studies find no causal link; violence rates fell as rap popularity rose. Country music with violent themes is not blamed for white violence. The criticism of rap is often coded racism against Black art forms.",
            "link": "https://journals.sagepub.com/doi/10.1177/0305735617752784"
        },
        {
            "text": "Black people are anti-police and want to defund everything.",
            "debunk": "Polls show Black Americans want police reform, not abolition. Most support redirecting some funds to mental health and social services, but still want armed police for violent crime. The 'defund' label is a media caricature.",
            "link": "https://www.pewresearch.org/short-reads/2020/09/02/most-americans-express-support-for-police-reform-proposals-while-little-support-for-defunding/"
        },
        {
            "text": "White genocide and replacement theory are real.",
            "debunk": "The white share of US population is declining due to lower birth rates, not replacement. No political movement seeks to eliminate white people. Replacement theory has led to multiple mass shootings (El Paso, Buffalo). It is a conspiracy theory with zero evidence.",
            "link": "https://www.adl.org/resources/backgrounders/great-replacement-theory"
        },
        {
            "text": "Nazism was a left‑wing ideology (National Socialist).",
            "debunk": "The Nazi party banned trade unions, privatised state industries, and violently suppressed communists and socialists. Hitler despised Marxism and imprisoned social democrats. The 'left‑wing Nazi' canard is a right‑wing talking point ignoring historical facts.",
            "link": "https://encyclopedia.ushmm.org/content/en/article/nazi-terror-begins"
        },
        {
            "text": "Black culture is the reason for poverty, not racism.",
            "debunk": "Cultural explanations fail when outcomes change with opportunity. Black immigrants from Africa and the Caribbean outperform native whites in education and income. The same 'culture' produces different results in different contexts, proving structural factors dominate.",
            "link": "https://www.nber.org/papers/w28222"
        },
        {
            "text": "Black people are more homophobic.",
            "debunk": "Support for same‑sex marriage among Black Americans is 51%, white support is 55% (Pew). The 4-point gap is smaller than age or education gaps within each race. Religious conservatism, not race, predicts opposition.",
            "link": "https://www.pewresearch.org/religion/fact-sheet/changing-attitudes-on-gay-marriage/"
        },
        {
            "text": "Black people don't value marriage.",
            "debunk": "Marriage rates are lower due to employment discrimination and mass incarceration removing Black men from communities, not values. Surveys show Black adults desire marriage at similar rates as white adults. Structural barriers, not culture, explain the gap.",
            "link": "https://www.brookings.edu/articles/the-black-white-marriage-gap/"
        },
        {
            "text": "Black people are oversensitive about race.",
            "debunk": "Perception of racism correlates with actual experiences of discrimination (audit studies). Calling out bias is a response to real events, not hypersensitivity. Denial of racism is more common than over‑reporting.",
            "link": "https://www.pnas.org/doi/10.1073/pnas.1706254114"
        },
        {
            "text": "Black women are angry (Sapphire stereotype).",
            "debunk": "Emotional expression ratings in blind studies (voice only, no race ID) show no difference. The stereotype disappears when race is unknown. It serves to delegitimise Black women's legitimate anger at injustice.",
            "link": "https://www.sciencedirect.com/science/article/pii/S002210311730691X"
        },
        {
            "text": "Black people don't read.",
            "debunk": "Literacy rates are identical when controlling for school quality. Black children's reading scores rise to white levels with the same phonics instruction. The gap is due to resource inequality, not interest.",
            "link": "https://www.journals.uchicago.edu/doi/10.1086/696621"
        },
        {
            "text": "Black people are bad at math.",
            "debunk": "Math gaps correlate with teacher quality and stereotype threat, not ability. Black students with the same instruction perform identically. Confidence and representation close the gap.",
            "link": "https://journals.sagepub.com/doi/10.3102/0162373719845658"
        }
    ]
}

total_tropes = sum(len(v) for v in tropes_data.values())

# ------------------------------------------------------------------
# COMPLETE HTML (UI, dark mode, search, AI)
# ------------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coalition for Truth – Debunk Anti‑Black Racism</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #0a0a0f;
            color: #eef;
            line-height: 1.6;
            transition: background 0.2s, color 0.2s;
        }
        body.light {
            background: #f5f7fc;
            color: #111;
        }
        .container {
            max-width: 1300px;
            margin: 0 auto;
            padding: 2rem 1.8rem;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 2.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        body.light header { border-bottom-color: rgba(0,0,0,0.1); }
        h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, #aaa);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            letter-spacing: -0.3px;
        }
        h1 i { margin-right: 8px; }
        .tagline {
            opacity: 0.7;
            margin-top: 0.3rem;
            font-size: 0.9rem;
        }
        .dark-toggle {
            background: rgba(255,255,255,0.08);
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            padding: 0.5rem 1rem;
            border-radius: 40px;
            transition: 0.2s;
        }
        .search-section {
            background: rgba(20,20,30,0.5);
            backdrop-filter: blur(8px);
            border-radius: 60px;
            padding: 0.5rem 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            border: 1px solid rgba(255,255,255,0.1);
        }
        body.light .search-section {
            background: rgba(255,255,255,0.6);
            border-color: rgba(0,0,0,0.08);
        }
        #searchInput {
            background: transparent;
            border: none;
            padding: 0.8rem 0;
            font-size: 1rem;
            color: inherit;
            width: 100%;
            outline: none;
        }
        .llm-card {
            background: rgba(25,25,35,0.7);
            backdrop-filter: blur(12px);
            border-radius: 32px;
            padding: 2rem;
            margin-bottom: 2.5rem;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        body.light .llm-card {
            background: rgba(255,255,255,0.7);
            border-color: rgba(0,0,0,0.08);
        }
        textarea {
            width: 100%;
            padding: 1rem;
            border-radius: 20px;
            border: 1px solid #444;
            background: #1e1e2a;
            color: #fff;
            font-family: inherit;
            resize: vertical;
            margin: 1rem 0;
        }
        body.light textarea {
            background: #fff;
            color: #111;
            border-color: #ccc;
        }
        .llm-buttons {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .btn {
            padding: 0.7rem 1.5rem;
            border: none;
            border-radius: 40px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
            font-size: 0.9rem;
        }
        .btn.primary {
            background: #2b6ef0;
            color: white;
            box-shadow: 0 2px 8px rgba(43,110,240,0.3);
        }
        .btn.secondary {
            background: rgba(255,255,255,0.12);
            color: #fff;
        }
        body.light .btn.secondary {
            background: #e2e8f0;
            color: #111;
        }
        .output-box {
            margin-top: 1.2rem;
            background: #00000055;
            padding: 1rem;
            border-radius: 20px;
            border-left: 4px solid #2b6ef0;
            font-size: 0.95rem;
            white-space: pre-wrap;
        }
        .copy-alert {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2ecc71;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 40px;
            font-size: 0.8rem;
            z-index: 1000;
        }
        .copy-alert.hidden { display: none; }
        .category {
            background: rgba(15,15,25,0.5);
            backdrop-filter: blur(6px);
            border-radius: 28px;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255,255,255,0.08);
            overflow: hidden;
        }
        body.light .category {
            background: rgba(255,255,255,0.5);
        }
        .category-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.2rem 1.8rem;
            cursor: pointer;
            background: rgba(0,0,0,0.2);
        }
        .category-header h2 { font-size: 1.4rem; font-weight: 600; margin: 0; }
        .count {
            font-size: 0.75rem;
            background: #2b6ef022;
            padding: 0.2rem 0.7rem;
            border-radius: 30px;
        }
        .trope-list {
            padding: 0.5rem 1rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .trope-card {
            background: rgba(30,30,45,0.4);
            border-radius: 20px;
            padding: 1.2rem;
            transition: 0.1s;
        }
        body.light .trope-card {
            background: rgba(0,0,0,0.02);
        }
        .trope-quote {
            font-weight: 500;
            margin-bottom: 0.75rem;
            font-style: italic;
        }
        .debunk-area {
            background: #0f2a1f;
            padding: 1rem;
            border-radius: 18px;
            margin: 0.75rem 0;
            color: #c0ffd0;
            font-size: 0.9rem;
            border-left: 3px solid #2ecc71;
        }
        body.light .debunk-area {
            background: #e0f2e5;
            color: #0b3b1f;
        }
        .source-link {
            display: inline-block;
            margin-top: 0.6rem;
            font-size: 0.75rem;
            color: #2ecc71;
            text-decoration: none;
        }
        .source-link:hover { text-decoration: underline; }
        .show-debunk-btn {
            background: none;
            border: 1px solid #2b6ef0;
            padding: 0.3rem 1rem;
            border-radius: 30px;
            color: #2b6ef0;
            cursor: pointer;
            font-size: 0.8rem;
        }
        footer {
            text-align: center;
            margin-top: 3rem;
            opacity: 0.5;
            font-size: 0.75rem;
        }
        .hidden { display: none; }
        @media (max-width: 700px) {
            .container { padding: 1rem; }
            h1 { font-size: 1.6rem; }
            .llm-buttons { flex-direction: column; }
        }
    </style>
</head>
<body>
<div class="container">
    <header>
        <div>
            <h1><i class="fas fa-scale-balanced"></i> Coalition for Truth</h1>
            <p class="tagline">Debunking anti-black racism with facts. This website and factsheet should prove useful for debunking hateful claims...</p>
        </div>
        <button id="darkModeToggle" class="dark-toggle"><i class="fas fa-moon"></i></button>
    </header>

    <div class="search-section">
        <i class="fas fa-search"></i>
        <input type="text" id="searchInput" placeholder="Search tropes... e.g., 'crime', 'IQ', 'welfare'">
    </div>

    <div class="llm-card">
        <h2><i class="fas fa-comment-dots"></i> AI Debunker – Paste any racist comment and/or claim of any kind.</h2>
        <p style="margin-top: 0.5rem;">Copy a claim from X, Reddit, 4chan, or any debate:</p>
        <textarea id="claimInput" rows="3" placeholder="Paste the racist claim here..."></textarea>
        <div class="llm-buttons">
            <button id="fullDebunkBtn" class="btn primary"><i class="fas fa-file-lines"></i> Full Debunk (600+ words)</button>
            <button id="shortReplyBtn" class="btn secondary"><i class="fas fa-reply-all"></i> Short Rebuttal (260 chars)</button>
        </div>
        <div id="llmOutput" class="output-box hidden"></div>
        <div id="copyAlert" class="copy-alert hidden">Copied ✓</div>
    </div>

    <div id="categoriesContainer">
        {% for category, trope_list in tropes.items() %}
        <div class="category" data-category="{{ category }}">
            <div class="category-header">
                <h2>{{ category }}</h2>
                <span class="count">{{ trope_list|length }} tropes</span>
                <i class="fas fa-chevron-down toggle-icon"></i>
            </div>
            <div class="trope-list hidden">
                {% for trope in trope_list %}
                <div class="trope-card" data-trope-text="{{ trope.text }}">
                    <div class="trope-quote">“{{ trope.text }}”</div>
                    <div class="debunk-area hidden">
                        <div class="debunk-text">{{ trope.debunk }}</div>
                        <a href="{{ trope.link }}" target="_blank" rel="noopener noreferrer" class="source-link">Source <i class="fas fa-external-link-alt"></i></a>
                    </div>
                    <button class="show-debunk-btn">Show Debunk <i class="fas fa-arrow-right"></i></button>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
    <footer>
        <p> Reach out to coalition.for.truth1@gmail.com for more inquiries.</p>
    </footer>
</div>
<script>
    const toggle = document.getElementById('darkModeToggle');
    toggle.addEventListener('click', () => {
        document.body.classList.toggle('light');
        const icon = toggle.querySelector('i');
        icon.classList.toggle('fa-moon');
        icon.classList.toggle('fa-sun');
    });

    document.querySelectorAll('.category-header').forEach(header => {
        header.addEventListener('click', () => {
            const list = header.parentElement.querySelector('.trope-list');
            const icon = header.querySelector('.toggle-icon');
            list.classList.toggle('hidden');
            icon.classList.toggle('fa-chevron-down');
            icon.classList.toggle('fa-chevron-up');
        });
    });

    document.querySelectorAll('.show-debunk-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const card = btn.closest('.trope-card');
            const area = card.querySelector('.debunk-area');
            area.classList.toggle('hidden');
            const icon = btn.querySelector('i');
            icon.classList.toggle('fa-arrow-right');
            icon.classList.toggle('fa-arrow-down');
        });
    });

    const search = document.getElementById('searchInput');
    const allCards = document.querySelectorAll('.trope-card');
    const categories = document.querySelectorAll('.category');
    search.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase().trim();
        allCards.forEach(card => {
            const text = card.getAttribute('data-trope-text').toLowerCase();
            card.style.display = (q === '' || text.includes(q)) ? '' : 'none';
        });
        categories.forEach(cat => {
            const visible = Array.from(cat.querySelectorAll('.trope-card')).some(c => c.style.display !== 'none');
            cat.style.display = (!visible && q !== '') ? 'none' : '';
        });
    });

    const fullBtn = document.getElementById('fullDebunkBtn');
    const shortBtn = document.getElementById('shortReplyBtn');
    const claimInput = document.getElementById('claimInput');
    const outputDiv = document.getElementById('llmOutput');
    const copyAlert = document.getElementById('copyAlert');

    async function callAI(endpoint, claim, isLong) {
        if (!claim.trim()) {
            outputDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Please paste a claim.';
            outputDiv.classList.remove('hidden');
            return;
        }
        outputDiv.classList.remove('hidden');
        outputDiv.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Generating ' + (isLong ? 'full debunk...' : 'short rebuttal...');
        try {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ claim: claim })
            });
            const data = await res.json();
            const text = data.debunk || data.reply || 'Error: ' + (data.error || 'Unknown');
            outputDiv.innerHTML = `<i class="fas fa-copy" style="cursor:pointer; margin-right:8px;" onclick="copyToClipboard(this)"></i> ${text.replace(/\\n/g, '<br>')}`;
        } catch (err) {
            outputDiv.innerHTML = 'API error. Check server.';
        }
    }

    fullBtn.addEventListener('click', () => callAI('/api/debunk_full', claimInput.value, true));
    shortBtn.addEventListener('click', () => callAI('/api/reply_short', claimInput.value, false));

    window.copyToClipboard = function(el) {
        const text = el.parentElement.innerText.replace('📋', '').trim();
        navigator.clipboard.writeText(text);
        copyAlert.classList.remove('hidden');
        setTimeout(() => copyAlert.classList.add('hidden'), 1500);
    };
</script>
</body>
</html>
"""

# ------------------------------------------------------------------
# FLASK ROUTES
# ------------------------------------------------------------------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, tropes=tropes_data, total_tropes=total_tropes)

@app.route('/api/debunk_full', methods=['POST'])
def debunk_full():
    data = request.get_json()
    claim = data.get('claim', '').strip()
    if not claim:
        return jsonify({'error': 'No claim provided'}), 400
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": "You are a fact‑based debunker. Write a thorough, well‑structured rebuttal to the racist claim. Use specific statistics, study citations, and logical reasoning. Aim for 600–800 words. Do not use emotional appeals or mention 'systemic racism'. Be direct, cold, and factual."},
            {"role": "user", "content": claim}
        ],
        "temperature": 0.4,
        "max_tokens": 2000,
    }
    try:
        resp = requests.post(REASONER_URL, headers=headers, json=payload, timeout=45)
        resp.raise_for_status()
        debunk = resp.json()['choices'][0]['message']['content'].strip()
        return jsonify({'debunk': debunk})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reply_short', methods=['POST'])
def reply_short():
    data = request.get_json()
    claim = data.get('claim', '').strip()
    if not claim:
        return jsonify({'error': 'No claim provided'}), 400
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Generate a factual rebuttal to a racist claim. Maximum 260 characters. No emojis. No empathy. Use a statistic or study. Output only the rebuttal text."},
            {"role": "user", "content": claim}
        ],
        "temperature": 0.5,
        "max_tokens": 80
    }
    try:
        resp = requests.post(CHAT_URL, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        reply = resp.json()['choices'][0]['message']['content'].strip()
        if len(reply) > 260:
            reply = reply[:257] + "..."
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"🔥 Coalition for Truth – Anti‑Black Racism Debunker")
    print(f"📚 Loaded {total_tropes} high‑impact tropes (no hygiene/disease).")
    print(f"🤖 Full debunk: 600+ words | Short reply: 260 chars")
    print(f"🌐 Running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
