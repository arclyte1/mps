package com.example.mps.model

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
