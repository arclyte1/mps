package com.example.mps.presentation.model

import com.example.mps.domain.model.Match

data class MatchView(
    val id: Long,
    val name: String,
) {

    companion object {
        fun fromMatch(match: Match) = MatchView(
            id = match.id,
            name = match.name ?: "Undefined",
        )
    }
}
