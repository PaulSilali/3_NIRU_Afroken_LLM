import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AGENTS, DATA_SOURCES, PERFORMANCE_TARGETS } from '@/constants/agents';
import * as Icons from 'lucide-react';
import { LucideIcon } from 'lucide-react';

export default function About() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-16 md:py-24 bg-gradient-to-br from-primary/10 via-background to-accent/5">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="max-w-4xl mx-auto text-center"
            >
              <h1 className="text-4xl md:text-5xl font-bold mb-6">
                About AfroKen LLM
              </h1>
              <p className="text-xl text-muted-foreground mb-4">
                A locally hosted, multilingual AI copilot transforming citizen-government interactions
              </p>
              <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
                AfroKen LLM addresses Kenya's public service delivery challenges by providing 
                instant, verified, multilingual responses to citizen queries—powered by advanced 
                AI trained on Kenyan government data.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Problem Statement */}
        <section className="py-16 container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-3xl font-bold mb-6">The Challenge</h2>
              <Card>
                <CardContent className="p-6 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <div className="text-4xl font-bold text-destructive mb-2">5+</div>
                      <p className="text-sm text-muted-foreground">
                        Average days for issue resolution in government contact centres
                      </p>
                    </div>
                    <div>
                      <div className="text-4xl font-bold text-warning mb-2">&lt;55%</div>
                      <p className="text-sm text-muted-foreground">
                        Citizen trust in online government responsiveness
                      </p>
                    </div>
                    <div>
                      <div className="text-4xl font-bold text-primary mb-2">100%</div>
                      <p className="text-sm text-muted-foreground">
                        Manual processing of repetitive queries consuming valuable resources
                      </p>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-border">
                    <h3 className="font-semibold mb-3">Three Structural Barriers:</h3>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <Badge variant="outline" className="mt-0.5">1</Badge>
                        <span><strong>Language & Accessibility Gaps:</strong> Most services are English-only, 
                        leaving millions of Swahili and indigenous language speakers underserved.</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Badge variant="outline" className="mt-0.5">2</Badge>
                        <span><strong>Data Fragmentation:</strong> Citizen feedback, policies, and FAQs 
                        exist in separate silos with no unified interface.</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Badge variant="outline" className="mt-0.5">3</Badge>
                        <span><strong>Manual Processing:</strong> Officers handle repetitive queries 
                        without intelligent assistance, reducing consistency.</span>
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </section>

        {/* AI Agent System */}
        <section className="py-16 bg-muted/30">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-3xl font-bold mb-4 text-center">Multi-Agent Architecture</h2>
              <p className="text-center text-muted-foreground mb-12 max-w-2xl mx-auto">
                AfroKen uses specialized AI agents working together to handle different aspects 
                of citizen service delivery
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
                {AGENTS.map((agent, index) => {
                  const Icon = Icons[agent.icon as keyof typeof Icons] as LucideIcon;
                  return (
                    <motion.div
                      key={agent.id}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.4, delay: index * 0.1 }}
                    >
                      <Card className="h-full">
                        <CardHeader>
                          <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                              {Icon && <Icon className="w-5 h-5 text-primary" />}
                            </div>
                            <div>
                              <CardTitle className="text-lg">{agent.name}</CardTitle>
                            </div>
                          </div>
                          <CardDescription>{agent.description}</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-1">
                            {agent.capabilities.map((capability) => (
                              <div key={capability} className="flex items-center gap-2 text-sm">
                                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                                <span>{capability}</span>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Expected Impact */}
        <section className="py-16 container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-3xl font-bold mb-4 text-center">Expected Impact</h2>
              <p className="text-center text-muted-foreground mb-12">
                Measurable improvements in service delivery and citizen satisfaction
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                  <CardContent className="p-6 text-center">
                    <div className="text-4xl font-bold text-success mb-2">
                      {PERFORMANCE_TARGETS.responseTimeReduction}%
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Reduction in average response time
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6 text-center">
                    <div className="text-4xl font-bold text-primary mb-2">
                      +{PERFORMANCE_TARGETS.satisfactionImprovement}%
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Improvement in satisfaction scores
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6 text-center">
                    <div className="text-4xl font-bold text-accent mb-2">
                      KES {(PERFORMANCE_TARGETS.annualSavings / 1000000).toFixed(0)}M
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Annual cost savings
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6 text-center">
                    <div className="text-4xl font-bold text-info mb-2">
                      {PERFORMANCE_TARGETS.newJobs.toLocaleString()}+
                    </div>
                    <p className="text-sm text-muted-foreground">
                      New digital-skills jobs created
                    </p>
                  </CardContent>
                </Card>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Data Sources */}
        <section className="py-16 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="text-3xl font-bold mb-4 text-center">Knowledge Base</h2>
                <p className="text-center text-muted-foreground mb-12">
                  AfroKen is trained on verified, official Kenyan government data sources
                </p>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      {DATA_SOURCES.map((source) => (
                        <div
                          key={source.name}
                          className="flex flex-col md:flex-row md:items-center justify-between p-4 rounded-lg bg-muted/50 gap-2"
                        >
                          <div>
                            <h3 className="font-semibold">{source.name}</h3>
                            <p className="text-sm text-muted-foreground">{source.coverage}</p>
                          </div>
                          <Badge variant="secondary" className="self-start md:self-auto">
                            {source.category}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Vision 2030 Alignment */}
        <section className="py-16 container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-3xl font-bold mb-6 text-center">Strategic Alignment</h2>
              
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Vision 2030 & National Strategies</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <h4 className="font-semibold mb-1">Vision 2030 Political Pillar</h4>
                      <p className="text-sm text-muted-foreground">
                        Enhances transparency and citizen participation in governance
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Digital Economy Blueprint (2020)</h4>
                      <p className="text-sm text-muted-foreground">
                        Promotes data-driven service delivery and digital inclusion
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">AI Strategy 2025-2030</h4>
                      <p className="text-sm text-muted-foreground">
                        Implements priority area #4: "Localized AI for Public Service Delivery"
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>UN Sustainable Development Goals</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Badge className="mb-2">SDG 9</Badge>
                        <p className="text-sm">
                          <strong>Industry, Innovation & Infrastructure:</strong> Builds digital 
                          public infrastructure through AI
                        </p>
                      </div>
                      <div>
                        <Badge className="mb-2">SDG 10</Badge>
                        <p className="text-sm">
                          <strong>Reduced Inequalities:</strong> Bridges language and 
                          accessibility gaps
                        </p>
                      </div>
                      <div>
                        <Badge className="mb-2">SDG 16</Badge>
                        <p className="text-sm">
                          <strong>Peace, Justice & Strong Institutions:</strong> Fosters 
                          transparent communication
                        </p>
                      </div>
                      <div>
                        <Badge className="mb-2">SDG 17</Badge>
                        <p className="text-sm">
                          <strong>Partnerships for Goals:</strong> Connects government, 
                          academia, and private AI labs
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </motion.div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
