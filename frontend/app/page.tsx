import Link from "next/link";
import { SiteHeader } from "./components/SiteHeader";

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-6xl px-6 pb-8 pt-6 sm:px-10">
        <SiteHeader />

        <section className="max-w-3xl pt-16 sm:pt-24">
          <p className="eyebrow">Free · Private · For teens & families</p>
          <h1 className="mt-5 text-5xl leading-[1.05] sm:text-7xl">
            From your lab panel <em className="italic text-[var(--clay-bright)]">to</em> your dinner table.
          </h1>
          <p className="mt-6 max-w-xl text-lg text-[var(--ink-soft)]">
            Panel to Table explains your lab results in plain language and suggests foods and recipes that fit them. It’s free, private, and built for teens and families.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/test" className="btn px-6 py-3">Start</Link>
            <a href="#how-it-works" className="btn btn-secondary px-6 py-3">See how it works</a>
          </div>
        </section>

        <img
          src="/home/bowl-eggs.png"
          alt="A bowl of quinoa, avocado, kale, sweet potato, and soft-boiled eggs"
          className="mt-12 h-[420px] w-full rounded-[28px] object-cover object-center sm:h-[540px]"
        />
      </div>

      <section className="mx-auto max-w-2xl px-6 py-20 text-center sm:px-10">
        <p className="eyebrow">01</p>
        <h2 className="mt-3 text-4xl sm:text-5xl">Understand your numbers</h2>
        <p className="mt-4 text-[var(--ink-soft)]">
          Type in your results and see which markers are in range and what each one means. Panel to Table uses the correct ranges for your age, including the separate ones for people under 20.
        </p>
      </section>

      <section className="mx-auto grid max-w-6xl items-center gap-8 px-6 sm:px-10 md:grid-cols-2 md:gap-14">
        <img
          src="/home/bowl-broccoli.png"
          alt="A bowl of broccoli, chickpeas, shredded greens, carrots, and lime"
          className="h-80 w-full rounded-[28px] object-cover"
        />
        <div>
          <p className="eyebrow">02</p>
          <h2 className="mt-3 text-4xl sm:text-5xl">Eat for your results</h2>
          <p className="mt-4 max-w-md text-[var(--ink-soft)]">
            Get food ideas and real recipes matched to what’s flagged, like iron-rich meals when your ferritin is low.
          </p>
        </div>
      </section>

      <section className="mx-auto mt-16 grid max-w-6xl items-center gap-8 px-6 sm:px-10 md:mt-24 md:grid-cols-2 md:gap-14">
        <div>
          <p className="eyebrow">03</p>
          <h2 className="mt-3 text-4xl sm:text-5xl">Know when to see a doctor</h2>
          <p className="mt-4 max-w-md text-[var(--ink-soft)]">
            Results that need a doctor’s attention are shown first, and Panel to Table never offers diet tips in place of care.
          </p>
        </div>
        <img
          src="/home/bowl-tofu.png"
          alt="A bowl of tofu, tomatoes, edamame, and eggs"
          className="h-80 w-full rounded-[28px] object-cover"
        />
      </section>

      <section className="mx-auto max-w-2xl px-6 py-20 text-center sm:px-10">
        <p className="eyebrow">04</p>
        <h2 className="mt-3 text-4xl sm:text-5xl">Private by design</h2>
        <p className="mt-4 text-[var(--ink-soft)]">
          There’s no account, and nothing is saved on our servers. Your history stays in your own browser.
        </p>
      </section>

      <section id="how-it-works" className="mx-auto max-w-6xl scroll-mt-8 px-6 sm:px-10">
        <h2 className="text-4xl">How it works</h2>
        <div className="mt-8 grid gap-8 md:grid-cols-3">
          <div>
            <p className="eyebrow">01</p>
            <h3 className="mt-2 text-2xl">Type in your results</h3>
            <p className="mt-2 text-[var(--ink-soft)]">Enter the markers on your report — no account needed.</p>
          </div>
          <div>
            <p className="eyebrow">02</p>
            <h3 className="mt-2 text-2xl">We read the numbers</h3>
            <p className="mt-2 text-[var(--ink-soft)]">Each marker is checked against the ranges for your age.</p>
          </div>
          <div>
            <p className="eyebrow">03</p>
            <h3 className="mt-2 text-2xl">Eat for your results</h3>
            <p className="mt-2 text-[var(--ink-soft)]">Get food ideas and recipes matched to what’s flagged.</p>
          </div>
        </div>
      </section>

      <div className="mx-auto mt-14 max-w-6xl px-6 sm:px-10">
        <img
          src="/home/dinner-spread.png"
          alt="A dinner table set with vegetables, grains, and plates"
          className="h-[420px] w-full rounded-[28px] object-cover sm:h-[520px]"
        />
      </div>

      <section className="mx-auto max-w-2xl px-6 py-20 text-center sm:px-10">
        <h2 className="text-4xl sm:text-5xl">Ready when you are.</h2>
        <p className="mt-4 text-[var(--ink-soft)]">
          Free, no account, and nothing is saved on our servers. Your history stays in your own browser.
        </p>
        <Link href="/test" className="btn mt-8 px-8 py-3">Start</Link>
      </section>

      <footer className="mx-auto max-w-2xl space-y-4 px-6 pb-16 text-center text-sm text-[var(--ink-soft)] sm:px-10">
        <p>
          Panel to Table is an educational tool, not medical advice. Ranges come from the{" "}
          <a className="text-link" href="https://ods.od.nih.gov/factsheets/VitaminD-HealthProfessional/" target="_blank" rel="noreferrer">NIH Office of Dietary Supplements</a>
          , the{" "}
          <a className="text-link" href="https://diabetes.org/about-diabetes/diagnosis" target="_blank" rel="noreferrer">American Diabetes Association</a>
          , and{" "}
          <a className="text-link" href="https://www.nhlbi.nih.gov/files/docs/guidelines/atp3xsum.pdf" target="_blank" rel="noreferrer">NHLBI</a>
          {" "}guidelines. Always talk to your doctor about your results.
        </p>
        <p>
          Also{" "}
          <a className="text-link" href="https://ods.od.nih.gov/factsheets/VitaminB12-HealthProfessional/" target="_blank" rel="noreferrer">vitamin B12</a>
          ,{" "}
          <a className="text-link" href="https://ods.od.nih.gov/factsheets/Iron-HealthProfessional/" target="_blank" rel="noreferrer">iron</a>
          , and the{" "}
          <a className="text-link" href="https://www.nhlbi.nih.gov/files/docs/guidelines/peds_guidelines_sum.pdf" target="_blank" rel="noreferrer">NHLBI pediatric lipid notes</a>
          . A meal plan is requested from Spoonacular and is not stored. A barcode lookup is requested from Open Food Facts and is not stored.
        </p>
        <p>© 2026 Panel to Table · Not a substitute for medical advice.</p>
      </footer>
    </div>
  );
}
