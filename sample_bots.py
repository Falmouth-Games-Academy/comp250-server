from db import db

sample_bots = {
    "_id": "Falmouth-Games-Academy+comp250-microrts",
    "status": "ready",
    #"repository": db.bots.find_one({"_id": "Falmouth-Games-Academy+comp250-bot"})["repository"],
    "class_names": [
        "ai.PassiveAI",
        "ai.RandomAI",
        "ai.RandomBiasedAI",
        "ai.abstraction.HeavyRush",
        "ai.abstraction.LightRush",
        "ai.abstraction.RangedRush",
        "ai.abstraction.WorkerRush",
#        "ai.abstraction.cRush.CRush_V1",
#        "ai.abstraction.cRush.CRush_V2",
        #"ai.abstraction.partialobservability.POHeavyRush",
        #"ai.abstraction.partialobservability.POLightRush",
        #"ai.abstraction.partialobservability.PORangedRush",
        #"ai.abstraction.partialobservability.POWorkerRush",
        #"ai.ahtn.AHTNAI",
        #"ai.core.ContinuingAI",
        #"ai.core.PseudoContinuingAI",
        #"ai.mcts.believestatemcts.BS1_NaiveMCTS",
        #"ai.mcts.believestatemcts.BS2_NaiveMCTS",
        #"ai.mcts.believestatemcts.BS3_NaiveMCTS",
        #"ai.mcts.informedmcts.InformedNaiveMCTS",
        #"ai.mcts.mlps.MLPSMCTS",
#        "ai.mcts.naivemcts.NaiveMCTS",
        #"ai.mcts.naivemcts.TwoPhaseNaiveMCTS",
        #"ai.mcts.naivemcts.TwoPhaseNaiveMCTSPerNode",
        #"ai.mcts.uct.DownsamplingUCT",
#        "ai.mcts.uct.UCT",
        #"ai.mcts.uct.UCTFirstPlayUrgency",
#        "ai.mcts.uct.UCTUnitActions",
        #"ai.minimax.ABCD.ABCD",
        #"ai.minimax.ABCD.IDABCD",
        #"ai.minimax.RTMiniMax.IDRTMinimax",
        #"ai.minimax.RTMiniMax.IDRTMinimaxRandomized",
        #"ai.minimax.RTMiniMax.RTMinimax",
        #"ai.montecarlo.MonteCarlo",
        #"ai.montecarlo.lsi.LSI",
#        "ai.portfolio.PortfolioAI",
        #"ai.portfolio.portfoliogreedysearch.PGSAI",
        #"ai.portfolio.portfoliogreedysearch.UnitScriptsAI",
        #"ai.puppet.BasicConfigurableScript",
        #"ai.puppet.PuppetNoPlan",
        #"ai.puppet.PuppetSearchAB",
        #"ai.puppet.PuppetSearchMCTS",
        #"ai.puppet.SingleChoiceConfigurableScript",
        #"ai.socket.SocketAI",
        #"ai.stochastic.UnitActionProbabilityDistributionAI",
        #"gui.MouseController",
    ]
}


