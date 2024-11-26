import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Mixed-Control',
    Svg: require('@site/static/img/AgentOrg-1.svg').default,
    description: (
      <>
        The agents are designed to handle different goals from user needs and builder objectives, ensuring more dynamic and goal-driven interactions.
      </>
    ),
  },
  {
    title: 'Compositional Task Organization',
    Svg: require('@site/static/img/AgentOrg-2.svg').default,
    description: (
      <>
        The complex real-world tasks are proposed to be broken down into modular, reusable components handled by each worker, enhancing efficiency and scalability.
      </>
    ),
  },
  {
    title: 'Human Intervention',
    Svg: require('@site/static/img/AgentOrg-3.svg').default,
    description: (
      <>
        Integrates human oversight and interactive refinement, ensuring critical decisions are accurate and user preferences are prioritized.
      </>
    ),
  },
  {
    title: 'Continual Learning',
    Svg: require('@site/static/img/AgentOrg-4.svg').default,
    description: (
      <>
        The agents evolve and improve over time by learning from interactions, maintaining their relevance and effectiveness in dynamic environments.
      </>
    ),
  }
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--3')}>
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
