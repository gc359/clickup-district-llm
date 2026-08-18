import { useState } from 'react'
import { postTicket } from '../../api.js'

const BUILDINGS = [
  'Bloomfield High School',
  'North Jr. High School',
  'South Jr. High School',
  'Carteret School',
  'Berkshire School',
  'Brookdale School',
  'Demarest School',
  'Fairview School',
  'Franklin School',
  'Oakview School',
  'Watsessing School',
  'Forest Glen School',
  'Board of Education',
  'Other',
]

const CATEGORIES = [
  'Hardware',
  'Software',
  'Network / WiFi',
  'Account / Password',
  'Printer',
  'Phone',
  'Other',
]

export default function TicketForm({ onCancel, onSubmitted, onError }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [building, setBuilding] = useState('')
  const [room, setRoom] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit() {
    const trimmedName = name.trim()
    const trimmedDescription = description.trim()

    if (!trimmedName || !trimmedDescription) {
      window.alert('Please fill in your name and a description.')
      return
    }

    setSubmitting(true)
    try {
      const ticket = await postTicket({
        name: trimmedName,
        email: email.trim() || null,
        building: building || null,
        room: room.trim() || null,
        // The mockup lets category go unselected; the backend requires one of
        // its known categories, so an unselected dropdown falls back to "Other".
        category: category || 'Other',
        description: trimmedDescription,
      })
      onSubmitted(ticket)
    } catch {
      setSubmitting(false)
      onError()
    }
  }

  return (
    <div className="ticket-form">
      <h4>Submit a Support Ticket</h4>

      <label htmlFor="tf-name">Your Name</label>
      <input
        id="tf-name"
        type="text"
        placeholder="First and last name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <label htmlFor="tf-email">Email</label>
      <input
        id="tf-email"
        type="email"
        placeholder="you@bloomfield.k12.nj.us"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <label htmlFor="tf-building">Building</label>
      <select id="tf-building" value={building} onChange={(e) => setBuilding(e.target.value)}>
        <option value="">Select building...</option>
        {BUILDINGS.map((b) => (
          <option key={b}>{b}</option>
        ))}
      </select>

      <label htmlFor="tf-room">Room Number</label>
      <input
        id="tf-room"
        type="text"
        placeholder="e.g. 204"
        value={room}
        onChange={(e) => setRoom(e.target.value)}
      />

      <label htmlFor="tf-category">Category</label>
      <select id="tf-category" value={category} onChange={(e) => setCategory(e.target.value)}>
        <option value="">Select category...</option>
        {CATEGORIES.map((c) => (
          <option key={c}>{c}</option>
        ))}
      </select>

      <label htmlFor="tf-desc">Description</label>
      <textarea
        id="tf-desc"
        placeholder="Describe the issue..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <div className="ticket-form-actions">
        <button className="ticket-submit" disabled={submitting} onClick={handleSubmit}>
          {submitting ? 'Submitting...' : 'Submit Ticket'}
        </button>
        <button className="ticket-cancel" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  )
}
