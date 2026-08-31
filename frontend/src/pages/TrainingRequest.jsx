import Header from '../components/Header.jsx'
import Hero from '../components/Hero.jsx'
import ClickUpFormEmbed from '../components/ClickUpFormEmbed.jsx'
import Footer from '../components/Footer.jsx'

const FORM_URL = 'https://forms.clickup.com/9014421433/f/8cmu9xt-8714/SI4KA8USV49RXV9RXR'

export default function TrainingRequest() {
  return (
    <>
      <Header />
      <main>
        <Hero
          title="Tech-ED Training"
          description="Request technology training or professional development using the form below."
        />
        <ClickUpFormEmbed src={FORM_URL} title="Tech-ED Training form" />
      </main>
      <Footer />
    </>
  )
}
