import Header from '../components/Header.jsx'
import Hero from '../components/Hero.jsx'
import ClickUpFormEmbed from '../components/ClickUpFormEmbed.jsx'
import Footer from '../components/Footer.jsx'

const FORM_URL = 'https://forms.clickup.com/9014421433/f/8cmu9xt-10294/LE7CAQHAKESP6J0KSD'

export default function IdRequest() {
  return (
    <>
      <Header />
      <main>
        <Hero
          title="ID Request"
          description="Order a new or replacement staff or student ID badge using the form below."
        />
        <ClickUpFormEmbed src={FORM_URL} title="ID Request form" />
      </main>
      <Footer />
    </>
  )
}
