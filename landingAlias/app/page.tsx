import { AuroraBackground } from "@/components/aurora-background"
import { Navbar } from "@/components/navbar"
import { HeroSection } from "@/components/hero-section"
import { MarqueeStrip } from "@/components/marquee-strip"
import { ProblemSection } from "@/components/problem-section"
import { HowItWorksSection } from "@/components/how-it-works-section"
import { UseCasesSection } from "@/components/use-cases-section"
import { DeveloperSection } from "@/components/developer-section"
import { YieldSection } from "@/components/yield-section"
import { CTASection } from "@/components/cta-section"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <>
      <AuroraBackground />
      <Navbar />
      <main>
        <HeroSection />
        <MarqueeStrip />
        <ProblemSection />
        <HowItWorksSection />
        <UseCasesSection />
        <DeveloperSection />
        <YieldSection />
        <CTASection />
      </main>
      <Footer />
    </>
  )
}
