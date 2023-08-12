package com.example.mps.model

import com.fasterxml.jackson.annotation.JsonProperty
import java.util.*

data class Match(

    @JsonProperty("id")
    val id: Long,

    @JsonProperty("name")
    val name: String?,

    @JsonProperty("start_time")
    val startTime: Date? = null,

    @JsonProperty("end_time")
    val endTime: Date? = null,

    @JsonProperty("games_count")
    val gamesCount: Int = 0,
)
