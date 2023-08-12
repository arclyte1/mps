package com.example.mps.controller

import com.example.mps.model.MatchView
import com.example.mps.service.MatchService
import org.springframework.stereotype.Controller
import org.springframework.ui.Model
import org.springframework.ui.set
import org.springframework.web.bind.annotation.GetMapping


@Controller
class HtmlController(
    private val service: MatchService
) {

    @GetMapping("/")
    fun index(model: Model): String {
        model["title"] = "Mps"
        model["matches"] = service.getMatches().map {MatchView.fromMatch(it)}
        return "index"
    }
}