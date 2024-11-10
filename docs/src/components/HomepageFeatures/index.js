import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Mixed-Initiative Framework',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Deliver personalized, accurate responses by treating each user as unique. 
        Go beyond generic, population-based insights through dynamic user interaction.
      </>
    ),
  },
  {
    title: 'All-in-One Controllable Task Management',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Streamline multiple tasks within a unified system based on <code>NLU</code>. 
        Powered by <code>TaskGraph</code>, different <code>Agents</code> manage specific tasks, 
        each broken down into best-practice steps for maximum control and efficiency.
      </>
    ),
  },
  {
    title: 'Iterative optimization',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Continuously improve <code>TaskGraph</code> performance using conversation history. 
        Refine processes for more efficient, customized guidance over time.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
