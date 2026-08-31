import { Wrench, Laptop } from 'lucide-react'
import Header from '../components/Header.jsx'
import Hero from '../components/Hero.jsx'
import ServiceCard from '../components/ServiceCard.jsx'
import Footer from '../components/Footer.jsx'

const ACTIONS = [
  {
    to: '/chromebook-repair',
    icon: Wrench,
    title: 'Chromebook Repair',
    desc: 'Device is damaged or malfunctioning and needs to be fixed.',
  },
  {
    to: 'https://bloomfieldk12.clickup.com/forms/9014421433/f/8cmu9xt-23694/MFLD5VDFT3651RIJ64',
    icon: Laptop,
    title: 'New/Replacement Device',
    desc: "Student needs a Chromebook or charger they don't currently have.",
    external: true,
  },
]

const STEPS = [
  {
    lead: 'Pick the right form.',
    body: 'Repair if the device is broken; New/Replacement if the student needs a device issued.',
  },
  {
    lead: 'Fill in student info and device details.',
    body: 'Serial number is on the bottom of the Chromebook near the barcode.',
  },
  {
    lead: 'Submit.',
    body: 'A ticket is created automatically and our IT team is notified immediately.',
  },
  {
    lead: "We'll follow up within 1 business day",
    body: 'to coordinate pickup, delivery, or next steps.',
  },
]

export default function MediaSpecialistHelpdesk() {
  return (
    <>
      <Header />
      <main>
        <Hero
          title="Chromebook Helpdesk"
          description="Media Specialist Portal &mdash; submit repair tickets or request devices for your students."
        />
        <div className="services">
          {ACTIONS.map((action) => (
            <ServiceCard key={action.title} {...action} />
          ))}
        </div>
        <section className="steps-section">
          <h2 className="section-heading">How it works</h2>
          <ol className="step-list">
            {STEPS.map((step) => (
              <li key={step.lead}>
                <strong>{step.lead}</strong> {step.body}
              </li>
            ))}
          </ol>
        </section>
        <p className="contact-callout">
          <strong>Need help?</strong> Contact IT directly or reach out to your building tech.
        </p>
      </main>
      <Footer />
    </>
  )
}
