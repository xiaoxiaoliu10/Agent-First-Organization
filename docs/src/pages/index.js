import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import arklexDiagram from '@site/static/img/AgentOrg-main.png';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <br></br>
        <br></br>
        <div className="row responsive-margin">
          <div className={clsx('col col--6')} style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '20px' }}>
            <div className={styles.buttons}>
              <Link
                className='button button--secondary button--lg black-button'
                href='https://pypi.org/project/arklex/'>
                  <svg height="20" preserveAspectRatio="xMidYMid" viewBox="0 0 256 255" width="20" xmlns="http://www.w3.org/2000/svg">
                    <linearGradient id="a" x1="12.959359%" x2="79.638833%" y1="12.039393%" y2="78.200854%">
                      <stop offset="0" stop-color="#387eb8"/><stop offset="1" stop-color="#366994"/>
                    </linearGradient>
                    <linearGradient id="b" x1="19.127525%" x2="90.741533%" y1="20.579181%" y2="88.429037%">
                      <stop offset="0" stop-color="#ffe052"/>
                      <stop offset="1" stop-color="#ffc331"/>
                    </linearGradient>
                    <path d="m126.915866.07227555c-64.8322829.00000462-60.7837372 28.11518925-60.7837372 28.11518925l.0722755 29.1270467h61.8678717v8.7453417h-86.4415589s-41.486166-4.7049094-41.486166 60.7114618c-.00000463 65.416358 36.2100508 63.096556 36.2100508 63.096556h21.6103896v-30.355731s-1.1648552-36.210051 35.6318464-36.210051h61.3619421s34.475438.557297 34.475438-33.3190286v-56.0135516c0-.0000047 5.234323-33.89723325-62.518352-33.89723325zm-34.1140591 19.58667415c6.1553999-.0000045 11.1304351 4.9750349 11.1304351 11.1304348.000004 6.1553999-4.9750352 11.1304348-11.1304351 11.1304348-6.1553999.0000046-11.1304348-4.9750349-11.1304348-11.1304348-.0000047-6.1553999 4.9750349-11.1304348 11.1304348-11.1304348z" fill="url(#a)"/><path d="m128.757101 254.126271c64.832302 0 60.783738-28.11519 60.783738-28.11519l-.072275-29.127046h-61.867872v-8.745342h86.441559s41.486166 4.704896 41.486166-60.711485c.000023-65.4163514-36.210051-63.0965491-36.210051-63.0965491h-21.61039v30.3557243s1.164874 36.2100508-35.631846 36.2100508h-61.361948s-34.475437-.557296-34.475437 33.319052v56.013552s-5.2343225 33.897233 62.518356 33.897233zm34.114059-19.586674c-6.155401 0-11.130434-4.975033-11.130434-11.130435 0-6.155403 4.975033-11.130435 11.130434-11.130435 6.155403 0 11.130435 4.975032 11.130435 11.130435.000023 6.155402-4.975032 11.130435-11.130435 11.130435z" fill="url(#b)"/>
                  </svg>
                  <span className={styles.pythonButtonText}>pip install arklex</span>
              </Link>
            </div>
            <div className={styles.buttons}>
              <Link
                className="button button--secondary button--lg"
                to='/docs/intro'>
                  Documentation
              </Link>
            </div>
          </div>
          
          <div className={clsx('col col--6')} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className={styles.buttons} style={{ alignItems: 'start'}}>
              <Link
                className="button button--secondary button--lg button-small"
                href='https://github.com/arklexai/Agent-First-Organization'>
                  <svg width={20} height={20} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="m0 0h24v24h-24z" fill="#fff" opacity="0" transform="matrix(-1 0 0 -1 24 24)"/><path d="m12 1a10.89 10.89 0 0 0 -11 10.77 10.79 10.79 0 0 0 7.52 10.23c.55.1.75-.23.75-.52s0-.93 0-1.83c-3.06.65-3.71-1.44-3.71-1.44a2.86 2.86 0 0 0 -1.22-1.58c-1-.66.08-.65.08-.65a2.31 2.31 0 0 1 1.68 1.11 2.37 2.37 0 0 0 3.2.89 2.33 2.33 0 0 1 .7-1.44c-2.44-.27-5-1.19-5-5.32a4.15 4.15 0 0 1 1.11-2.91 3.78 3.78 0 0 1 .11-2.84s.93-.29 3 1.1a10.68 10.68 0 0 1 5.5 0c2.1-1.39 3-1.1 3-1.1a3.78 3.78 0 0 1 .11 2.84 4.15 4.15 0 0 1 1.17 2.89c0 4.14-2.58 5.05-5 5.32a2.5 2.5 0 0 1 .75 2v2.95s.2.63.75.52a10.8 10.8 0 0 0 7.5-10.22 10.89 10.89 0 0 0 -11-10.77" fill="#231f20"/></svg>
                  <span className='margin-left-sm'>Source Code</span>
              </Link>
            </div>
            <div className={styles.buttons}>
              <Link
                className="button button--secondary button--lg button-small"
                href='https://discord.gg/jpZs3GqnTG'>
                  <svg width={20} fill="#7289da" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><rect height="512" rx="15%" width="512"/><path d="m346 392-21-25c41-11 57-39 57-39-52 49-194 51-249 0 0 0 14 26 56 39l-23 25c-70-1-97-48-97-48 0-104 46-187 46-187 47-33 90-33 90-33l3 4c-58 16-83 42-83 42 68-46 208-42 263 0 1-1-33-28-86-42l5-4s43 0 90 33c0 0 46 83 46 187 0 0-27 47-97 48z" fill="#fff"/><ellipse cx="196" cy="279" rx="33" ry="35"/><ellipse cx="312" cy="279" rx="33" ry="35"/></svg>
                  <span className='margin-left-sm'>Get Connected</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main>
        <div style={{ margin: '40px 8%'}}>
          <div className='row' style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '90px 0 50px 0'}}>
            <div className='col col--6'>
              <img src={arklexDiagram} alt="Arklex Diagram" />
            </div>
            <div className='col col--6'>
              <iframe 
                width="100%"
                height='300px'
                src="https://www.loom.com/embed/f5a45bcc8c834ec998083eaf7793a912?sid=7525fc12-ffd2-403c-9623-cab087bb2ced" 
                title="Arklex: The Future of AI Agents" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen
                webkitallowfullscreen>
              </iframe>
            </div>
          </div>
            <p style={{textAlign: "center"}}>AI is no longer just about automation—it’s about intelligent collaboration between humans and machines. 
            Arklex redefines AI agents by ensuring goal alignment, structured decision-making, and continuous adaptability. 
            As AI continues to transform industries, Arklex stands at the forefront of the next-generation AI revolution. </p>
          <div style={{ display: 'flex', justifyContent: 'center'}}>
            <Link className='button button--secondary button--md'
            href='https://www.arklex.ai/qa/blogs/57526a0e-7803-4452-96f3-53995394accd'>
              Read more 🚀
            </Link>
          </div>
        </div>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
