import Header from '../components/Header.jsx'
import Hero from '../components/Hero.jsx'
import ServicesGrid from '../components/ServicesGrid.jsx'
import Footer from '../components/Footer.jsx'

export default function Landing() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <ServicesGrid />
      </main>
      <Footer />
    </>
  )
}
